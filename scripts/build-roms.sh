#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$ROOT"
games=(FIRERED LEAFGREEN)
clean=0
baseline=0
for argument in "$@"; do
    case "$argument" in
        --firered) games=(FIRERED);;
        --leafgreen) games=(LEAFGREEN);;
        --clean) clean=1;;
        --baseline) baseline=1;;
        --help|-h) echo 'Usage: ./scripts/build-roms.sh [--firered|--leafgreen] [--clean] [--baseline]'; exit 0;;
        *) echo "Unknown option: $argument" >&2; exit 2;;
    esac
done
mkdir -p dist logs .build-deps
if ! mkdir .build-deps/rom-build.lock 2>/dev/null; then
    echo 'Another ROM build is running. If a previous process was killed, remove .build-deps/rom-build.lock.' >&2; exit 1;
fi
stage=""
cleanup() {
    result=$?
    if [[ -n "$stage" ]]; then rm -rf "$stage"; fi
    rmdir .build-deps/rom-build.lock
    if ((result)); then
        for game in "${games[@]}"; do
            if [[ "$game" == FIRERED ]]; then label=FireRed; else label=LeafGreen; fi
            rm -f "dist/Pokemon-$label-Mods.gba"
        done
        rm -f dist/manifest.json
        echo 'Build failed. Selected ROM outputs removed; see diagnostics above and logs/.' >&2
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
# Remove published artifacts before any prerequisite check can fail.
# Baseline runs publish no mod ROMs, so their prior manifest is invalid too.
rm -f dist/manifest.json dist/patches.json dist/verification.json dist/SHA256SUMS dist/*.bps
for game in "${games[@]}"; do
    if [[ "$game" == FIRERED ]]; then label=FireRed; else label=LeafGreen; fi
    rm -f "dist/Pokemon-$label-Mods.gba" "dist/Pokemon-$label-Mods.json"
    if ((baseline)); then rm -f ".build-deps/baselines/Pokemon-$label-Original.gba"; fi
done
[[ -x tools/agbcc/bin/agbcc && -n "$MAKE" ]] || { echo 'Run ./scripts/setup.sh first.' >&2; exit 1; }
for binary in arm-none-eabi-as arm-none-eabi-cpp arm-none-eabi-ld arm-none-eabi-objcopy python3; do
    command -v "$binary" >/dev/null || { echo "Missing $binary; run setup." >&2; exit 1; }
done
if ((clean)); then "$MAKE" clean > logs/clean.log 2>&1; mkdir -p dist; fi
stage=$(mktemp -d "$ROOT/dist/.build.XXXXXX")
trap 'echo "ROM build/verification failed at line $LINENO; see logs/. No selected outputs were published." >&2' ERR
jobs=${JOBS:-$(getconf _NPROCESSORS_ONLN || echo 2)}
for game in "${games[@]}"; do
    if [[ "$game" == FIRERED ]]; then label=FireRed; build=firered; else label=LeafGreen; build=leafgreen; fi
    echo "Building $label (MODS=$((1-baseline)))..."
    "$MAKE" -j"$jobs" GAME_VERSION="$game" MODS="$((1-baseline))" > "logs/build-$build.log" 2>&1 || { tail -80 "logs/build-$build.log" >&2; exit 1; }
    python3 scripts/verify-rom.py "poke$build.gba" "$game" "$baseline"
    if ((baseline)); then
        python3 - "$build" <<'PY'
import hashlib, pathlib, sys
name=sys.argv[1]
expected=pathlib.Path(name+'.sha1').read_text().split()[0]
actual=hashlib.sha1(pathlib.Path('poke'+name+'.gba').read_bytes()).hexdigest()
assert actual == expected, f'Baseline mismatch: {actual} != {expected}'
print('Exact upstream baseline SHA-1 passed:', name)
PY
        cp "poke$build.gba" "$stage/Pokemon-$label-Original.gba"
    else
        cp "poke$build.gba" "$stage/Pokemon-$label-Mods.gba"
        if [[ -x .build-deps/emulator-driver ]]; then
            python3 tests/advanced.py "poke$build.gba" "poke$build.elf" "$build" > "logs/emulator-$build.log" 2>&1 || { tail -80 "logs/emulator-$build.log" >&2; exit 1; }
        else
            echo 'Emulator tests unavailable: run scripts/setup-emulator.sh (ROM integrity checked).'
        fi
    fi
done
if ((baseline)); then
    mkdir -p .build-deps/baselines
    for output in "$stage"/*.gba; do mv "$output" .build-deps/baselines/; done
else
    for output in "$stage"/*.gba; do mv "$output" dist/; done
    python3 scripts/build-manifest.py
fi
echo 'All selected builds and available verification passed.'
