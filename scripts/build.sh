#!/bin/bash
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BUILD_DIR=$(dirname "$SCRIPT_DIR")
WORK_DIR="$BUILD_DIR/work"
OUT_DIR="$BUILD_DIR/out"
ISO_ROOT="$BUILD_DIR/iso_root"
command -v mkarchiso >/dev/null || { echo 'Install archiso first.' >&2; exit 1; }
(( EUID == 0 )) || { echo "Run with sudo: $0" >&2; exit 1; }
# Refresh and package sources as the invoking user before cleaning any build output.
[[ -n ${SUDO_USER:-} && $SUDO_USER != root ]] || {
    echo 'Invoke with sudo from a regular user account so makepkg can run safely.' >&2; exit 1;
}
runuser -u "$SUDO_USER" -- "$SCRIPT_DIR/build-packages.sh"
# Do not delete a work tree containing active mounts; stop and report them.
if findmnt -rn -o TARGET | awk -v path="$WORK_DIR" '$0 == path || index($0, path "/") == 1 { found=1 } END { exit !found }'; then
    echo "Active mounts under $WORK_DIR; unmount them before rebuilding." >&2
    exit 1
fi
rm -rf -- "$WORK_DIR"
mkdir -p "$WORK_DIR" "$OUT_DIR"
# Generate the host-side Pacman configuration; the ISO keeps the public URL.
PACMAN_CONF=$(mktemp "$WORK_DIR/pacman-build.XXXXXXXX.conf")
trap 'rm -f -- "$PACMAN_CONF"' EXIT
python "$SCRIPT_DIR/prepare-pacman.py" "$ISO_ROOT/pacman.conf" "$BUILD_DIR/ZelixRepo" "$PACMAN_CONF"
cd "$ISO_ROOT"
mkarchiso -C "$PACMAN_CONF" -v -L zelix -w "$WORK_DIR" -o "$OUT_DIR" "$ISO_ROOT"
echo "Build completed; ISO output: $OUT_DIR"
