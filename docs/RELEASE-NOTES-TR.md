# ZelixOS Aurora 1.0.1 Sürüm Notları

## Yenilikler ve iyileştirmeler

- Zelixins'e birden fazla masaüstü ortamı ve pencere yöneticisini aynı kurulumda seçme desteği eklendi: KDE Plasma, GNOME, Xfce, Hyprland, Sway, i3 ve bspwm.
- Masaüstü seçim ekranına önizlemeler eklendi. Giriş yöneticisi seçenekleri seçilen ortamlarla uyumlu olacak şekilde düzenlendi ve kurulum özeti tüm seçimleri gösterecek biçimde güncellendi.
- Masaüstlerine ve pencere yöneticilerine özel başlangıç görünümü ve duvar kâğıtları eklendi.
- Hyprland seçildiğinde Waybar ve Wofi kuruluyor. Waybar oturumla birlikte başlıyor; **Super + Space** uygulama menüsünü açıyor.
- Disk, bölüm ve önyükleme uyumluluğu kontrolleri ile BIOS ve UEFI kurulumlarının yapılandırması iyileştirildi. Kurulum ve kurulum sonrası yapılandırma hatalarının bildirilmesi geliştirildi.
- Zelix Updater'a güncellenebilir paketleri sürümleriyle listeleme, güncelleme öncesi onay alma ve işlem çıktısını gösterme özellikleri eklendi.
- Kurulu sistemde güncelleme kontrolünün başlatılmasını engelleyebilen eksik `pacman-contrib` ve `fakeroot` bağımlılıkları giderildi. Eksik komut durumundaki hata mesajı açıklandı.
- Canlı ve kurulu sistemdeki ZelixOS dokümantasyon, destek ve hata bildirim bağlantıları güncellendi.
- Zelix uygulamalarında ek optimizasyonlar yapıldı.

**Kurulum notu:** Kurucu seçilen diskin tamamını siler ve manuel bölümleme sunmaz. Kurulumdan önce önemli dosyalarınızı yedekleyin.
