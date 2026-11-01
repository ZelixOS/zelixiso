# Çoklu masaüstü seçimi ve görünüm

Zelixins 1.2.0 içinde masaüstleri ayrı bir sayfadan seçilir. En az bir seçim gerekir.
Kurulum özeti bütün seçimleri gösterir; archinstall `Desktop.details` listesine her
profil ayrı yazılır. Masaüstleri giriş ekranından seçilebilen ayrı oturumlardır.

## Görselleri ekleme

Esas kaynak `zelixins/` klasörüdür. Paketleme kopyasını doğrudan düzenlemeyin.

| Masaüstü | Ekran görüntüsü | Duvar kâğıdı |
| --- | --- | --- |
| KDE Plasma | `previews/kde-plasma.png` | Mevcut otomatik Aurora; ayrı görsel gerekmez |
| GNOME | `previews/gnome.png` | `backgrounds/gnome/wallpaper.png` |
| Xfce | `previews/xfce.png` | `backgrounds/xfce/wallpaper.png` |
| Hyprland | `previews/hyprland.png` | `backgrounds/hyprland/wallpaper.png` |
| Sway | `previews/sway.png` | `backgrounds/sway/wallpaper.png` |
| i3 | `previews/i3.png` | `backgrounds/i3/wallpaper.png` |
| bspwm | `previews/bspwm.png` | `backgrounds/bspwm/wallpaper.png` |

`.jpg`, `.jpeg`, `.webp` uzantıları da desteklenir. Aynı adın birden fazla uzantısı
varsa sırasıyla PNG, JPG, JPEG, WebP seçilir. Bitmiş görselleri bu dosya adlarıyla koyun.
Ekran görüntülerine veya duvar kâğıdı önizlemesine tıklanınca büyük görüntü açılır.
Kurucu açıkken eklenen görseller yaklaşık iki saniye içinde yeniden okunur.

Eksik/okunamayan önizlemede yer tutucu gösterilir. Eksik veya bozuk duvar kâğıdında
mevcut Zelix Aurora görseli kullanılır. Yeni görseller çalışmakta olan eski ISO'ya
kendiliğinden aktarılmaz; kaynakları eşitleyip paketi ve ISO'yu yeniden üretmek gerekir.
Kurulum sırasında slayt gösterisi yoktur.

## Giriş yöneticisi politikası

Bu tablo kurucunun sunduğu, bilinçli olarak sınırlı kombinasyonlardır; listelenmeyen
bir çiftin hiçbir yöntemle çalışamayacağı iddiası değildir. "Önerilen" ile "seçilebilir"
ayrıdır. Gerçek kurulum ve oturum açma doğrulaması BIOS/UEFI sanal makinelerinde yapılmalıdır.

| Masaüstü | Önerilen | Seçilebilir |
| --- | --- | --- |
| KDE Plasma | SDDM | SDDM, GDM, Ly |
| GNOME | GDM | GDM, SDDM, Ly |
| Xfce4 | LightDM | LightDM, SDDM, GDM, Ly |
| Hyprland | SDDM | SDDM, Ly |
| Sway | SDDM | SDDM, Ly |
| i3-wm | LightDM | LightDM, SDDM, GDM, Ly |
| bspwm | LightDM | LightDM, SDDM, GDM, Ly |

Birden fazla seçimde yalnızca kümelerin kesişimi sunulur. Geçerli bir greeter seçimi
korunur; yeni DE ile uyumsuz olursa ortak öneriye dönülür ve sayfada açıklanır.
Ortak seçenek yoksa ileri düğmesi kapanır. JSON üretiminde de aynı doğrulama yapılır.

Kaynaklar: [SDDM](https://github.com/sddm/sddm),
[Hyprland giriş yöneticileri](https://wiki.hypr.land/getting-started/master-tutorial/),
[Ly oturum ve servis belgeleri](https://github.com/fairyglade/ly).
Hyprland belgelerindeki ilk oturum sorunu nedeniyle GDM bu kurucuda Hyprland için
sunulmaz. X11'e yönelik LightDM seçeneği Wayland profillerinde sunulmaz.
Kurulu archinstall kaynakları çoklu profil serileştirmesi ve Ly servis adı için de
kontrol edilmiştir; Ly yeni sürümlerde `ly@tty1` ile çalışır, ilgili getty kapatılır.
Eski `ly.service` birimi varsa kurulum sonrası kod onu kullanabilir.

## DE'ye özel görünüm

| DE | İlk varsayılanlar |
| --- | --- |
| KDE | Zelix Aurora global görünümü, beyaz aksan, mevcut otomatik Aurora duvar kâğıdı |
| GNOME | Koyu görünüm, destekleniyorsa slate aksan, açık/koyu duvar kâğıdı |
| Xfce | Materia-dark, Adwaita ikonları, monitör/çalışma alanı duvar kâğıtları |
| Hyprland | Beyaz odak çerçevesi, pencere boşlukları, yuvarlatma, swaybg duvar kâğıdı |
| Sway | Beyaz odak çerçevesi, boşluklar, output duvar kâğıdı |
| i3 | Beyaz odak çerçevesi, boşluklar, feh duvar kâğıdı |
| bspwm | Beyaz odak çerçevesi, boşluklar, feh duvar kâğıdı |

Seçilen görseller `/usr/share/wallpapers/Zelix/<de>/` altına kopyalanır.
Makine seçimi ve duvar kâğıdı eşlemesi `/etc/zelix/desktops.json` içinde tutulur.
KDE, GNOME ve Xfce ayarları yalnızca kendi oturumlarında, kullanıcı başına bir defa
uygulanır. Başarı işareti yazılmadan hata olursa sonraki girişte yeniden denenir.
GNOME/Xfce logları `~/.local/state/zelix/appearance-<de>.log` içindedir.

Pencere yöneticilerinde mevcut varsayılan tuş atamaları korunur; kullanıcı
konfigürasyonuna ayrı Zelix dosyası dahil edilir. Bu dosyalar tekrar oluşturulup
kullanıcının değişiklikleri ezilmez. Duvar kâğıdını her oturumda yükleyen komut da
normal kullanıcı konfigürasyonunun parçasıdır; kullanıcı buradan değiştirebilir.
Hyprland'ın kurulu sürümüne göre Lua veya eski hyprlang biçimi kullanılır.

Global `~/.config/gtk-3.0/settings.ini` gibi paylaşılan GTK dosyaları yazılmaz.
DE'lerin kendi tercih sistemleri ve kendi config klasörleri kullanılır.
Paketler başka giriş yöneticileri getirse bile yalnızca seçilen servis etkinleştirilir.

## Doğrulama

Testler 127 masaüstü alt kümesinin tamamında greeter kesişimini ve çoklu profil
JSON'unu kontrol eder. Arayüzde seçim değişimi, boş seçim, geç eklenen/bozuk görsel,
dil değişimi ve beyaz ileri düğmesi doğrulanır. Görünüm testleri gerçek diske ve
mevcut masaüstünün ayarlarına dokunmayan geçici dizinlerle çalışır.

Yerel kurulumda varsa archinstall profil ayrıştırıcısı ve Hyprland
`--verify-config` kontrolü de çalıştırılır. Bunlar gerçek oturum/VM testinin yerini tutmaz.

Kurulu SDDM yapılandırması canlı oturumun otomatik girişini veya sabit Plasma
oturumunu taşımaz. Canlı ISO otomatik girişi ayrı tutulur; greeter kendi varsayılan
ekran sunucusuyla açılıp seçilen X11/Wayland kullanıcı oturumunu başlatır.
