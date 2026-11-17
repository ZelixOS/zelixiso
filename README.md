# ZelixOS

ZelixOS, Arch Linux tabanlı bir Linux dağıtımıdır. Bu çalışma alanı canlı ISO profilini, uygulama kaynaklarını ve paket üretim araçlarını içerir.

## Dizinler

| Dizin | İçerik |
| --- | --- |
| `iso_root/` | Archiso profili ve canlı sistem dosyaları |
| `zelixins/` | Grafik kurucu |
| `zelix-hello/` | Karşılama ve sistem yönetimi uygulaması |
| `zelix-updater/` | Sistem güncelleme uygulaması |
| `zelixpen/` | Ekran üzerinde çizim aracı |
| `zelix-repo/` | Paket tarifleri ve paketleme kaynakları |
| `scripts/` | Kaynak eşitleme, paketleme ve ISO üretimi |
| `tests/`, `docs/` | Otomatik kontroller ve geliştirme belgeleri |

## Derleme

Arch Linux veya ZelixOS üzerinde `archiso`, `base-devel` ve ilgili PKGBUILD dosyalarındaki bağımlılıklar gereklidir. Çalışma alanının yolu boşluk içermemelidir.

Paketleri normal kullanıcıyla oluşturun:

```bash
scripts/build-packages.sh
```

ISO oluşturun:

```bash
sudo scripts/build.sh
```

Paketler `ZelixRepo/`, ISO dosyaları `out/` dizinine yazılır. Derleme sırasında `work/` yeniden oluşturulur.

## Geliştirme

Uygulama değişikliklerini ana kaynak dizinlerinde yapın. Paketleme kopyalarını eşitlemek ve kontrolleri çalıştırmak için:

```bash
python scripts/sync-sources.py
python scripts/sync-sources.py --check
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
```

Disk kurulumu ve önyükleme kontrollerini sanal makinede yapın. Ayrıntılar [geliştirme rehberinde](docs/DEVELOPMENT.md) bulunur.

## Bağlantılar

- [Web sitesi](https://zelixos.com/)
- [ISO yayınları](https://github.com/ZelixOS/zelixiso/releases)
- [Paket deposu](https://github.com/ZelixOS/zelix-repo/releases/tag/stable)
