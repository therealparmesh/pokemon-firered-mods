#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
source "$ROOT/config/dependencies.env"
cd "$ROOT"
for binary in git c++; do
    command -v "$binary" >/dev/null || { echo "Missing $binary; run make setup." >&2; exit 1; }
done
[[ -n "$MAKE" ]] || { echo 'Missing GNU make; run make setup.' >&2; exit 1; }
mkdir -p .build-deps logs
if [[ ! -d .build-deps/flips/.git ]]; then
    git clone https://github.com/Alcaro/Flips.git .build-deps/flips
fi
if [[ "$(git -C .build-deps/flips rev-parse HEAD)" != "$FLIPS_REVISION" ]]; then
    git -C .build-deps/flips checkout --detach "$FLIPS_REVISION"
    "$MAKE" -C .build-deps/flips TARGET=cli clean > logs/setup-flips.log 2>&1
fi
"$MAKE" -C .build-deps/flips TARGET=cli CFLAGS=-O2 > logs/setup-flips.log 2>&1 || { tail -60 logs/setup-flips.log >&2; exit 1; }
echo 'Pinned Floating IPS command-line patcher ready.'
