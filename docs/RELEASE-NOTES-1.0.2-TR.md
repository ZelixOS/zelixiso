# ZelixOS Aurora 1.0.2 Sürüm Notları

Aurora 1.0.2; daha esnek, on ekranlı bir kurulum akışı, Zelix uygulamalarında İspanyolca desteği ve güncellenmiş sistem araçları sunar.

## Yenilikler

- Zelix Installer 1.3.0; Minimal, Standard, Full Experience ve Custom profillerini sunar. Kurulumdan önce isteğe bağlı uygulamalar ve Aurora görünüm bileşenleri seçilebilir.
- Kurucu arayüzü İngilizce, Türkçe ve İspanyolca destekler. Arayüz dili, kurulan sistem için seçilen dilden bağımsızdır.
- KDE Plasma, GNOME, Xfce, Hyprland, Sway, i3 veya bspwm; uyumlu giriş yöneticileri ve masaüstü önizlemeleriyle seçilebilir.
- Kök bölüm için Ext2/3/4, Btrfs, XFS veya F2FS ve isteğe bağlı ayrı bir `/home` bölümü içeren otomatik disk planı incelenebilir. Disk ve bölüm doğrulaması iyileştirilmiştir.
- Çekirdekler, önyükleyici, yansılar, kullanıcı hesapları ve ek paketler seçilebilir; kurulum başlamadan önce yapılandırmanın tamamı gözden geçirilir.
- Zelix Hello 1.2.0, Zelix Updater 1.2.0 ve Zelix CLI 1.3.0 yenilenmiş arayüzler ve İspanyolca desteği getirir.

## İndirme ve doğrulama

[Birleşik x86_64 ISO dosyasını indirin](https://sourceforge.net/projects/zelixos/files/zelix_isos/zelixos-2026.11.22-x86_64.iso/download). ISO 22 Kasım 2026'da oluşturulmuştur; boyutu 2.914.713.600 bayttır (yaklaşık 2,71 GiB).

```text
SHA-256  85197cf008bf47b037f87d181d4c31d2f278a6bbc9caedffd02fe3efd21cb71a
Dosya    zelixos-2026.11.22-x86_64.iso
```

İndirdikten sonra `sha256sum zelixos-2026.11.22-x86_64.iso` komutunu çalıştırıp sonucu yukarıdaki değerle karşılaştırın. ISO'yu en az 8 GB kapasiteli bir USB belleğe yazın ve kurucuyu açmadan önce internete bağlanın.

**Kurulum uyarısı:** Otomatik disk planı seçilen diskin tamamını siler. Dosyalarınızı yedekleyin ve disk özetini kontrol edin. Bu sürümde elle bölüm düzenleme ve disk şifreleme yoktur.

Bileşen depolarıyla birlikte etiketli kaynağı almak için `git clone --recurse-submodules --branch 1.0.2 https://github.com/ZelixOS/zelixiso.git` komutunu kullanın.
