#!/usr/bin/env python3
"""Exercise real build failure cleanup in disposable repositories."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
for flags, retained in [([], None), (['--firered'], 'LeafGreen'), (['--leafgreen'], 'FireRed')]:
    with tempfile.TemporaryDirectory(prefix='frlg-build-failure-') as directory:
        root = Path(directory)
        (root / 'scripts').mkdir()
        (root / 'dist').mkdir()
        for name in ('env.sh', 'build-roms.sh'):
            shutil.copy2(ROOT / 'scripts' / name, root / 'scripts' / name)
        for game in ('FireRed', 'LeafGreen'):
            (root / 'dist' / f'Pokemon-{game}-Mods.gba').write_bytes(b'stale output')
        for name in ('manifest.json', 'patches.json', 'verification.json', 'SHA256SUMS', 'Pokemon-FireRed-Mods.bps', 'Pokemon-LeafGreen-Mods.bps'):
            (root / 'dist' / name).write_text('stale release output')
        env = dict(os.environ)
        env.pop('MAKE', None)
        result = subprocess.run([str(root / 'scripts/build-roms.sh'), *flags],
                                cwd=root, env=env, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 or 'setup.sh' not in result.stderr:
            raise AssertionError(f'Expected actionable prerequisite failure: {result}')
        expected = [] if retained is None else [f'Pokemon-{retained}-Mods.gba']
        actual = sorted(p.name for p in (root / 'dist').iterdir())
        if actual != expected or (root / '.build-deps/rom-build.lock').exists():
            raise AssertionError(f'Failure left stale outputs or a build lock: {actual}')
        print('PASS: missing prerequisites remove selected stale outputs, manifest and lock:', flags or 'both')
