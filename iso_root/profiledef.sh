#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="zelixos"
iso_label="ZELIX_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="ZelixOS <https://lanierc.github.io/zelixos>"
iso_application="ZelixOS Live/Rescue DVD"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="zelix"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.systemd-boot')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(	
  ["/etc/passwd"]="0:0:644"
  ["/etc/group"]="0:0:644"
  ["/etc/gshadow"]="0:0:400"
  ["/etc/os-release"]="0:0:644"
  ["/etc/sudoers.d/zelix"]="0:0:440"
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/zelix-init"]="0:0:755"
  ["/usr/local/bin/zelix"]="0:0:755"
  ["/usr/local/bin/zelix-first-login"]="0:0:755"
  ["/etc/xdg/autostart/zelix-hello.desktop"]="0:0:755"
  ["/etc/xdg/autostart/zelix-firstrun-wallpaper.desktop"]="0:0:755"
  ["/etc/skel/Desktop/zelix-installer.desktop"]="0:0:755"
)

