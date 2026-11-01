#!/usr/bin/env python3
"""Refresh derived packaging copies. Root app folders and iso_root are authoritative."""
import argparse
import filecmp
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'__pycache__', '.git', 'pkg', 'src'}

def files(path):
    if path.is_file():
        yield path, Path(path.name)
    else:
        for source in sorted(path.rglob('*')):
            relative = source.relative_to(path)
            if source.is_file() and not SKIP.intersection(relative.parts) and source.suffix != '.pyc':
                yield source, relative

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report drift without writing')
    args = parser.parse_args()
    for relative in ('zelixins/myself.py', 'zelix-hello/main.py', 'zelix-updater/main.py',
                     'zelix-repo/zelixins/PKGBUILD', 'iso_root/profiledef.sh'):
        if not (ROOT / relative).is_file():
            parser.error('Missing source: ' + relative +
                         '. Run: git submodule update --init --recursive')
    pairs = []
    def tree(source, destination):
        path = ROOT / source
        for source_file, relative in files(path):
            pairs.append((source_file, ROOT / destination / relative))
    def single(source, destination):
        pairs.append((ROOT / source, ROOT / destination))
    # Reusable installer assets: the live profile is the master for appearance.
    for path in ('etc/skel/.config', 'usr/share/color-schemes', 'usr/share/plasma/look-and-feel'):
        tree('iso_root/airootfs/' + path, 'zelixins/zelixdeps/' + path)
    for path in ('etc/xdg/autostart/zelix-firstrun-wallpaper.desktop', 'usr/local/bin/zelix-first-login'):
        single('iso_root/airootfs/' + path, 'zelixins/zelixdeps/' + path)
    # App sources are copied into packages and the offline installer payload.
    for app in ('zelix-hello', 'zelix-updater'):
        paths = ('main.py', 'zelix-updater.desktop', 'zelix-updater.png') if app == 'zelix-updater' else (
            'main.py', 'tabs', 'ui', 'utils', 'assets', 'zelix-hello.desktop',
            'readme.txt', 'readme_tr.txt', 'readme_en.txt')
        for path in paths:
            if (ROOT/app/path).is_dir():
                tree(f'{app}/{path}', f'zelix-repo/{app}/{path}')
                tree(f'{app}/{path}', f'zelixins/zelixdeps/usr/share/{app}/{path}')
            else:
                single(f'{app}/{path}', f'zelix-repo/{app}/{path}')
                # Desktop/icon locations already exist in the payload; sync those too.
                if path.endswith('.desktop'):
                    single(f'{app}/{path}', f'zelixins/zelixdeps/usr/share/applications/{path}')
                elif path.endswith('.png'):
                    for folder in ('zelix', 'pixmaps'):
                        single(f'{app}/{path}', f'zelixins/zelixdeps/usr/share/{folder}/{path}')
                else:
                    single(f'{app}/{path}', f'zelixins/zelixdeps/usr/share/{app}/{path}')
    # Copy helper/script/UI + the now-refreshed payload into the packaging repository.
    for path in ('myself.py', 'installer_support.py', 'zelix_post_install.sh', 'zelix-installer.desktop',
                 'icons', 'zelixdeps'):
        if (ROOT/'zelixins'/path).is_dir():
            # Resolve this tree after the first synchronization pass below.
            continue
        single('zelixins/' + path, 'zelix-repo/zelixins/' + path)
    def apply(pairs):
        changed = []
        for source, destination in pairs:
            if not destination.exists() or not filecmp.cmp(source, destination, shallow=False) or (
                source.stat().st_mode & 0o777) != (destination.stat().st_mode & 0o777):
                changed.append(str(destination.relative_to(ROOT)))
                if not args.check:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
        return changed
    drift = apply(pairs)
    pairs = []
    for path in ('icons', 'zelixdeps'):
        tree('zelixins/' + path, 'zelix-repo/zelixins/' + path)
    drift += apply(pairs)
    for name in drift:
        print(('DRIFT ' if args.check else 'UPDATED ') + name)
    if args.check and drift:
        raise SystemExit(1)
    print('Source copies are synchronized.' if not drift else f'{len(drift)} files updated/requiring update.')

if __name__ == '__main__':
    main()
