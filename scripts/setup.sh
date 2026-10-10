#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
source "$ROOT/config/dependencies.env"
trap 'echo "Setup failed at line $LINENO. Fix the diagnostic above and rerun ./scripts/setup.sh." >&2' ERR
cd "$ROOT"
if [[ "$(uname -s)" == Darwin ]]; then
    command -v brew >/dev/null || { echo 'Install Homebrew (https://brew.sh), then rerun setup.' >&2; exit 1; }
    xcrun --find clang >/dev/null || { echo 'Install Xcode Command Line Tools: xcode-select --install' >&2; exit 1; }
    packages=()
    for entry in 'arm-none-eabi-gcc:arm-none-eabi-cpp' 'make:gmake' 'libpng:pkg-config' 'pkgconf:pkg-config' 'cmake:cmake'; do
        package=${entry%%:*}; binary=${entry#*:}
        if ! command -v "$binary" >/dev/null 2>&1; then packages+=("$package"); fi
    done
    if ((${#packages[@]})); then HOMEBREW_NO_AUTO_UPDATE=1 brew install "${packages[@]}"; fi
    source "$ROOT/scripts/env.sh"
fi
missing=()
for binary in git cc c++ python3 perl pkg-config arm-none-eabi-as arm-none-eabi-ar arm-none-eabi-cpp arm-none-eabi-ld arm-none-eabi-objcopy; do
    command -v "$binary" >/dev/null || missing+=("$binary")
done
[[ -n "$MAKE" ]] || missing+=(GNU-make)
if ((${#missing[@]})); then
    echo "Missing prerequisites: ${missing[*]}" >&2
    echo 'Debian/Ubuntu: sudo apt-get install build-essential git gcc-arm-none-eabi binutils-arm-none-eabi libpng-dev pkg-config python3 cmake' >&2
    exit 1
fi
pkg-config --exists libpng || { echo 'Missing libpng development files. Install libpng-dev or brew install libpng.' >&2; exit 1; }
mkdir -p .build-deps logs
if [[ ! -d .build-deps/agbcc/.git ]]; then git clone https://github.com/pret/agbcc.git .build-deps/agbcc; fi
if [[ "$(git -C .build-deps/agbcc rev-parse HEAD)" != "$AGBCC_REVISION" ]]; then
    git -C .build-deps/agbcc checkout --detach "$AGBCC_REVISION"
fi
if [[ ! -x tools/agbcc/bin/agbcc || ! -x tools/agbcc/bin/old_agbcc || ! -x tools/agbcc/bin/agbcc_arm || ! -f tools/agbcc/lib/libc.a || ! -f tools/agbcc/lib/libgcc.a || ! -f .build-deps/agbcc.installed || "$(cat .build-deps/agbcc.installed)" != "$AGBCC_REVISION" ]]; then
    echo 'Building pinned agbcc; detailed log: logs/setup-agbcc.log'
    (cd .build-deps/agbcc && ./build.sh && ./install.sh ../..) > logs/setup-agbcc.log 2>&1 || { tail -60 logs/setup-agbcc.log >&2; exit 1; }
    echo "$AGBCC_REVISION" > .build-deps/agbcc.installed
fi
"$MAKE" -f make_tools.mk > logs/setup-tools.log 2>&1 || { tail -60 logs/setup-tools.log >&2; exit 1; }
{
    echo "pret=$PRET_REVISION agbcc=$AGBCC_REVISION"
    uname -sm
    arm-none-eabi-as --version | head -1
    arm-none-eabi-cpp --version | head -1
    cc --version | head -1
    pkg-config --modversion libpng
} > .build-deps/toolchain.txt
./scripts/setup-emulator.sh
echo 'Setup complete. Run make roms or ./scripts/build-roms.sh.'
