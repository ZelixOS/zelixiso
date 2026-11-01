# ZelixOS ISO build environment

Archiso profile and build tooling for ZelixOS Aurora (x86_64, KDE Plasma live desktop).

## Clone

```bash
git clone --recurse-submodules https://github.com/ZelixOS/zelixiso.git
cd zelixiso
```

For an existing checkout:

```bash
git submodule update --init --recursive
```

Each submodule is pinned to a commit. Updating this repository does not silently
switch application sources to the latest development branch.

## Build requirements

Use an updated Arch Linux x86_64 host, a checkout path without whitespace, an
internet connection, and enough free disk space for the live filesystem and ISO.
The build needs root privileges; package creation runs as the user invoking sudo.

```bash
sudo pacman -S --needed archiso base-devel git python python-pyqt6 qt6-svg qt6-imageformats \
  archinstall arch-install-scripts polkit util-linux
```

These commands install build tools on the host. The ISO package list is maintained
separately in `iso_root/packages.x86_64`.

## Build

Build the application packages and a complete local Pacman repository:

```bash
scripts/build-packages.sh
```

Build an ISO, rebuilding those packages first:

```bash
sudo scripts/build.sh
```

The script refuses an active mount under `work/`, then recreates that temporary
build directory. Existing files in `out/` are retained. `makepkg` never runs as root.
The local repository URL is generated from the checkout location; no developer
home directory is required. The installed/live system uses the public stable URL.

## Repository layout

| Path | Purpose |
| --- | --- |
| `iso_root/` | Archiso profile, live root filesystem, boot and appearance assets |
| `scripts/` | Source synchronization, package creation, ISO production |
| `tests/` | Installer policy and isolated KDE appearance checks |
| `docs/` | Development and validation notes |
| `zelixins/` | Installer source submodule |
| `zelix-hello/` | Welcome/maintenance source submodule |
| `zelix-updater/` | Updater source submodule |
| `zelix-repo/` | Package recipes and unchanged bootstrap packages submodule |
| `ZelixRepo/` | Generated local Pacman repository; ignored by Git |
| `work/`, `out/` | Temporary build filesystem and ISO output; ignored by Git |

Modify applications in their respective repositories and commit their changes
there before advancing the submodule pointers here. `sync-sources.py` refreshes
derived packaging copies; it does not commit or push them.

## Installer desktop choices

Zelixins supports installing several desktop sessions together. The dedicated selection
page shows descriptions, optional screenshots, and only login managers common to the
chosen desktops. KDE retains its existing automatic Aurora wallpaper; other desktops
accept optional wallpapers in their own source folders.

See the [desktop and artwork guide](docs/DESKTOPS.md) for filenames and appearance settings.

## Validate

```bash
python scripts/sync-sources.py --check
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

Appearance tests use private configuration directories. Full BIOS/UEFI installation
and a real KDE session still need VM testing after ISO production.

See [development notes](docs/DEVELOPMENT.md) for installer behavior and logs.

## Downloads

- [Pacman packages and indexes](https://github.com/ZelixOS/zelix-repo/releases/tag/stable)
- [ISO releases](https://github.com/ZelixOS/zelixiso/releases)

Generated package archives, ISO images, working files, caches, and local backups
are not committed to this repository.
