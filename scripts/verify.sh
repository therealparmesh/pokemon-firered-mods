#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$ROOT"
python3 tests/pipeline_failures.py
for game in FIRERED LEAFGREEN; do
    if [[ "$game" == FIRERED ]]; then label=FireRed; build=firered; else label=LeafGreen; build=leafgreen; fi
    python3 scripts/verify-rom.py "dist/Pokemon-$label-Mods.gba" "$game"
    [[ -x .build-deps/emulator-driver ]] || { echo 'Run make setup for emulator testing.' >&2; exit 1; }
    python3 tests/advanced.py "dist/Pokemon-$label-Mods.gba" "poke$build.elf" "$build"
done
