# ZelixOS Aurora 1.0.1 Release Notes

## What's new and improved

- Added support in Zelixins for selecting multiple desktop environments and window managers in a single installation: KDE Plasma, GNOME, Xfce, Hyprland, Sway, i3, and bspwm.
- Added previews to the desktop selection screen. Display manager choices now reflect compatibility with the selected environments, and the installation summary lists all selections.
- Added initial appearance settings and wallpapers tailored to each desktop environment and window manager.
- Hyprland installations now include Waybar and Wofi. Waybar starts with the session, and **Super + Space** opens the application launcher.
- Improved disk, partition, and boot compatibility checks and the configuration of BIOS and UEFI installations. Reporting of installation and post-installation configuration errors has also been improved.
- Added a list of available packages and their versions, update confirmation, and process output to Zelix Updater.
- Fixed missing `pacman-contrib` and `fakeroot` dependencies that could prevent update checks on installed systems. The error message for a missing command is now clearer.
- Updated the ZelixOS documentation, support, and bug-reporting links in the live and installed systems.
- Made additional optimizations to Zelix applications.

**Installation note:** The installer erases the entire selected disk and does not offer manual partitioning. Back up important files before installing.
