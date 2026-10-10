#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$ROOT"
mkdir -p .build-deps dist
if ! mkdir .build-deps/patch-build.lock 2>/dev/null; then
    echo 'Another patch build is running; inspect .build-deps/patch-build.lock.' >&2; exit 1
fi
stage=''
cleanup() {
    result=$?
    if [[ -n "$stage" ]]; then rm -rf "$stage"; fi
    rmdir .build-deps/patch-build.lock
    if ((result)); then
        rm -f dist/*.bps dist/patches.json
        echo 'Patch build failed; no patch outputs were retained.' >&2
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
rm -f dist/*.bps dist/patches.json dist/verification.json dist/SHA256SUMS
./scripts/setup-patcher.sh
./scripts/build-roms.sh --baseline
./scripts/build-roms.sh
stage=$(mktemp -d "$ROOT/dist/.patches.XXXXXX")
for label in FireRed LeafGreen; do
    base=".build-deps/baselines/Pokemon-$label-Original.gba"
    target="dist/Pokemon-$label-Mods.gba"
    patch="$stage/Pokemon-$label-Mods.bps"
    .build-deps/flips/flips --create --bps "$base" "$target" "$patch"
    .build-deps/flips/flips --apply "$patch" "$base" "$stage/$label.gba"
    cmp "$target" "$stage/$label.gba" || { echo "$label patch does not reproduce the tested ROM." >&2; exit 1; }
done
python3 - "$stage" <<'PY'
import hashlib, json, pathlib, sys
stage = pathlib.Path(sys.argv[1])
patches = {}
for game, label in [('firered', 'FireRed'), ('leafgreen', 'LeafGreen')]:
    target = pathlib.Path(f'dist/Pokemon-{label}-Mods.gba')
    baseline = pathlib.Path(f'.build-deps/baselines/Pokemon-{label}-Original.gba')
    result = json.loads(pathlib.Path(f'tests/output/{game}/results.json').read_text())
    target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    assert target_hash == result['rom_sha256'], f'{label} has no matching emulator verification'
    baseline_sha1 = hashlib.sha1(baseline.read_bytes()).hexdigest()
    assert baseline_sha1 == pathlib.Path(game + '.sha1').read_text().split()[0]
    name = f'Pokemon-{label}-Mods.bps'
    patches[name] = {'patch_sha256': hashlib.sha256((stage/name).read_bytes()).hexdigest(),
                     'original_sha1': baseline_sha1, 'output_sha256': target_hash,
                     'round_trip_matches_tested_rom': True}
(stage/'patches.json').write_text(json.dumps({'patches': patches,
    'dependencies': pathlib.Path('config/dependencies.env').read_text()}, indent=2)+'\n')
PY
mv "$stage"/*.bps "$stage/patches.json" dist/
echo 'Both BPS patches reproduce the emulator-tested ROMs exactly.'
