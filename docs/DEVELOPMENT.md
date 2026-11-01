# ZelixOS geliştirme ve doğrulama

## Kaynak düzeni

- `zelixins/`, `zelix-hello/`, `zelix-updater/`: uygulamaların esas kaynakları.
- `iso_root/airootfs/`: canlı sistem ve ortak görünüm varlıklarının esas kaynağı.
- `zelix-repo/`: ayrı Git deposu; paket tarifleri ve eşitlenen paketleme kaynakları.
- `ZelixRepo/`: ISO üretiminin kullandığı yerel paket deposu.
- `zelixins/zelixdeps/`: kurucunun çevrimdışı uygulama/görünüm yükü.

`python scripts/sync-sources.py` kaynakları paketleme ve kurucu kopyalarına aktarır.
`python scripts/sync-sources.py --check` farklılıkta başarısız olur ve dosya değiştirmez.
Uygulama kopyalarını doğrudan düzenlemeyin. PKGBUILD dosyalarını `zelix-repo/` içinde düzenleyin.
Alt Git depoları korunmuştur; üst depoya otomatik staging veya commit yapılmaz.
Üst `.gitignore` üretim çıktıları, paket arşivleri, yedekler ve önbellekleri dışarıda tutar.

## Paket ve ISO üretimi

Normal kullanıcı olarak:

```bash
scripts/build-packages.sh
```

Bu komut sabitlenen `zelix-repo` içindeki ortak paketleri alır, üç uygulamayı
yerel kaynaklardan paketler ve yalnızca `ZelixRepo/` içinde tam bir depo indeksi
oluşturur. Kaynak alt depolardaki indeksleri değiştirmez; internete yayın yapmaz.
Hello paketinin kaynağı artık hareketli bir uzak Git dalından alınmaz.

ISO üretimi:

```bash
sudo scripts/build.sh
```

Bu komut paketleri çağıran normal kullanıcıyla üretir, aktif mount varsa durur,
eski `work/` üretim dizinini yeniden oluşturur ve yeni ISO'yu `out/` içine yazar.
Mevcut ISO'ları silmez. Yerel depo adresi klonun konumundan üretilir ve
`mkarchiso -C` ile kullanılır; profili veya canlı sistemin depo adresini değiştirmez.
Pacman yerel dosya adresleri nedeniyle klon yolu boşluk içermemelidir.

## Kurulum ve görünüm

Kurucu diski tamamen siler; manuel bölümleme sunmaz. Gerçek disk ve boyut kontrolü,
bağlı bölüm kontrolü ve BIOS/önyükleyici uyumluluk kontrolü yapılır.
BIOS için GRUB ve ext4 `/boot`, UEFI için FAT32 ESP oluşturulur.
Birden fazla çekirdeğe göre boot alanı ayrılır; çok küçük ayrı `/home` oluşturulmaz.

`zelix_post_install.sh` yalnızca başarılı archinstall işleminden sonra çalışır.
Kök, boot ve varsa ayrı home bölümünü bağlar. KDE ayarları yalnızca KDE'ye,
SDDM ayarları yalnızca SDDM'ye uygulanır. Multilib seçimi korunur.
Mevcut initramfs kancaları korunarak Plymouth eklenir.
Paket, mount veya initramfs hatası kurucuya başarısızlık olarak döner.

KDE'de ilk giriş:

1. `org.zelixos.aurora.desktop` global görünümü uygulanır.
2. `ZelixAurora` renk şeması uygulanır.
3. Beyaz aksan **ayrı bir komutla** uygulanır. Plasma aracının aksan modu,
   aynı komutta verilen renk şeması argümanını uygulamaz.
4. Aksan seçimi kalıcı yazılır ve duvar kâğıdı uygulanır.
5. Tam başarıdan sonra kullanıcıya özel işaret oluşturulur.

Log: `~/.local/state/zelix/appearance.log` (XDG_STATE_HOME varsa o kullanılır).
Başarı işareti: `~/.local/state/zelix/aurora-v1.done`.
Başarısız girişte sonraki KDE oturumunda yeniden denenir. Başarılı kurulumdan sonra
kullanıcının tema tercihlerine tekrar müdahale edilmez; KDE dışındaki oturumlar atlanır.
Kurucunun logu arayüzde gösterilen `/tmp/zelix-install-*.log` dosyasıdır.

## Kontroller

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
python scripts/sync-sources.py --check
```

Testler gerçek diske dokunmaz. Yapılandırma matrisi, bölüm sınırları, multilib,
kurulum sonucu, ilk girişte hata/yeniden deneme ve kullanıcı başına tek çalıştırmayı
kontrol eder. Plasma araçları kuruluysa ayrı HOME/config ve erişilemeyen bir oturum
veriyoluyla gerçek renk şeması ve aksan yazımı da doğrulanır.

Canlı KDE oturumunun görsel sonucu, yeniden başlatma ve uçtan uca BIOS/UEFI kurulumu
ayrıca sanal makinede doğrulanmalıdır. Bu kontroller birim testlerinin kapsamı dışındadır.

## Kaynak sürümleri ve çıktılar

`git clone --recurse-submodules` veya `git submodule update --init --recursive`
ile bu deponun sabitlediği dört kaynak deposunu indirin. Alt depoları açıkça
istemeden `--remote` ile ilerletmeyin; bu işlem ISO kaynak sürümlerini değiştirir.

`work/`, `out/`, `ZelixRepo/`, paket arşivleri ve yerel yedekler üst depoya eklenmez.
Paketler `ZelixOS/zelix-repo` stable yayınından, yayımlanan ISO'lar `ZelixOS/zelixiso`
Releases bölümünden dağıtılır. Bu kaynak yüklemesi yeni bir ISO üretmez.

Calamares yapılandırmaları ve eski Calamares'e özel `zelix-postinstall` betikleri
bu kaynak yapısında bulunmaz. Önceki çalışma alanındaki yerel yedekler GitHub'a yüklenmez.
