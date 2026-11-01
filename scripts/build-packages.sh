#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if (( EUID == 0 )); then
    echo 'Run build-packages.sh as your regular user (makepkg refuses root).' >&2
    exit 1
fi
for tool in python makepkg repo-add; do
    command -v "$tool" >/dev/null || { echo "Missing build dependency: $tool" >&2; exit 1; }
done
python "$ROOT/scripts/sync-sources.py"
mkdir -p "$ROOT/ZelixRepo"
# The pinned package submodule contains the unchanged bootstrap packages.
# Do not copy an old application package into the newly generated index.
bootstrap_list=$(python - "$ROOT" <<'PY'
import filecmp, shutil, sys
from pathlib import Path
root = Path(sys.argv[1])
for source in sorted((root/'zelix-repo/x86_64').glob('*.pkg.tar.*')):
    if not source.name.endswith(('.pkg.tar.zst', '.pkg.tar.xz')):
        continue
    if source.name.startswith(('zelixins-', 'zelix-hello-', 'zelix-updater-')):
        continue
    target = root/'ZelixRepo'/source.name
    if not target.exists() or not filecmp.cmp(source, target, shallow=False):
        shutil.copy2(source, target)
    print(target)
PY
)
mapfile -t bootstrap_packages <<< "$bootstrap_list"
# A fresh clone must have these custom dependencies as well as the three apps.
for app in yay paru mkinitcpio-openswap; do
    found=false
    for package in "${bootstrap_packages[@]}"; do
        if [[ $(basename "$package") == "$app"-[0-9]* ]]; then found=true; fi
    done
    [[ $found == true ]] || { echo "Missing bootstrap package: $app (initialize submodules)." >&2; exit 1; }
done
packages=("${bootstrap_packages[@]}")
for app in zelix-hello zelix-updater zelixins; do
    (
        cd "$ROOT/zelix-repo/$app"
        PKGDEST="$ROOT/ZelixRepo" makepkg --force --cleanbuild --noconfirm
    )
    package_list=$(cd "$ROOT/zelix-repo/$app" && PKGDEST="$ROOT/ZelixRepo" makepkg --packagelist)
    while IFS= read -r package; do
        [[ -f $package ]] || { echo "Missing package: $package" >&2; exit 1; }
        packages+=("$package")
    done <<< "$package_list"
done
# Build a fresh index so obsolete app versions cannot accidentally reappear.
INDEX_DIR=$(mktemp -d "$ROOT/ZelixRepo/.index.XXXXXXXX")
trap 'rm -rf -- "$INDEX_DIR"' EXIT
repo-add "$INDEX_DIR/zelixrepo.db.tar.gz" "${packages[@]}"
python - "$ROOT/ZelixRepo" "$INDEX_DIR" "${packages[@]}" <<'PY'
import hashlib, os, shutil, sys
from pathlib import Path
repository, index = map(Path, sys.argv[1:3])
for filename in ('zelixrepo.db.tar.gz', 'zelixrepo.files.tar.gz'):
    os.replace(index/filename, repository/filename)
for filename in ('zelixrepo.db', 'zelixrepo.files'):
    temporary = repository/(filename + '.new')
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(filename + '.tar.gz')
    os.replace(temporary, repository/filename)
for name in sys.argv[3:]:
    package = Path(name)
    with package.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    package.with_suffix(package.suffix + '.sha256').write_text(digest + '  ' + package.name + '\n')
PY
