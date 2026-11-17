# ZelixOS

ZelixOS is an Arch Linux based distribution. This workspace contains the live ISO profile, application sources, and package build tools.

## Project structure

| Directory | Contents |
| --- | --- |
| `iso_root/` | Archiso profile and live system files |
| `zelixins/` | Graphical installer |
| `zelix-hello/` | Welcome and system management application |
| `zelix-updater/` | System update application |
| `zelixpen/` | On-screen drawing tool |
| `zelix-repo/` | Package recipes and packaging sources |
| `scripts/` | Source synchronization, packaging, and ISO build tools |
| `tests/`, `docs/` | Automated checks and development documentation |

## Building

Use Arch Linux or ZelixOS with `archiso`, `base-devel`, and the dependencies listed in the package recipes. The workspace path must not contain spaces.

Build packages as a regular user:

```bash
scripts/build-packages.sh
```

Build an ISO:

```bash
sudo scripts/build.sh
```

Packages are written to `ZelixRepo/` and ISO images to `out/`. The ISO build recreates `work/`.

## Development

Edit applications in their main source directories. Synchronize packaging copies and run checks with:

```bash
python scripts/sync-sources.py
python scripts/sync-sources.py --check
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
```

Test disk installation and boot behavior in a virtual machine. See the [development guide](docs/DEVELOPMENT.md) for details.

## Links

- [Website](https://zelixos.com/)
- [ISO releases](https://github.com/ZelixOS/zelixiso/releases)
- [Package repository](https://github.com/ZelixOS/zelix-repo/releases/tag/stable)
