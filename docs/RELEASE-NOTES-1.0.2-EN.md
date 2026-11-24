# ZelixOS Aurora 1.0.2 Release Notes

Aurora 1.0.2 adds a more flexible ten-screen installation flow, Spanish support across Zelix applications, and updated system tools.

## Highlights

- Zelix Installer 1.3.0 offers Minimal, Standard, Full Experience, and Custom profiles. You can choose optional applications and Aurora appearance components before installation.
- The installer interface supports English, Turkish, and Spanish. Its language can differ from the locale chosen for the installed system.
- Choose KDE Plasma, GNOME, Xfce, Hyprland, Sway, i3, or bspwm, with compatible login-manager options and desktop previews.
- Review an automatic disk layout with Ext2/3/4, Btrfs, XFS, or F2FS for the root filesystem and an optional separate `/home` partition. Disk and partition verification is improved.
- Choose kernels, bootloader, mirrors, user accounts, and additional packages; review the complete configuration before starting installation.
- Zelix Hello 1.2.0, Zelix Updater 1.2.0, and Zelix CLI 1.3.0 bring refreshed interfaces and Spanish support.

## Download and verify

[Download the unified x86_64 ISO](https://sourceforge.net/projects/zelixos/files/zelix_isos/zelixos-2026.11.22-x86_64.iso/download). The ISO was built on November 22, 2026 and is 2,914,713,600 bytes (about 2.71 GiB).

```text
SHA-256  85197cf008bf47b037f87d181d4c31d2f278a6bbc9caedffd02fe3efd21cb71a
File     zelixos-2026.11.22-x86_64.iso
```

Run `sha256sum zelixos-2026.11.22-x86_64.iso` after downloading and compare the result with the value above. Write the ISO to an 8 GB or larger USB drive and connect to the internet before starting the installer.

**Installation warning:** The automatic layout erases the entire selected disk. Back up your files and check the disk summary. Manual partition editing and disk encryption are not available in this release.

To check out the tagged source with its component repositories, use `git clone --recurse-submodules --branch 1.0.2 https://github.com/ZelixOS/zelixiso.git`.
