#!/usr/bin/env python3
"""Extended input-driven coverage; checkpoints come from this ROM's acceptance run."""
import hashlib, json, pathlib, runpy, signal, sys
from emulator import Emulator, ROOT
rom,elf,variant=sys.argv[1:]
ns=runpy.run_path(str(ROOT/'tests/acceptance.py'),run_name='__main__')
# runpy returns a copy; helpers retain the original module globals.
ns=ns['open_menu'].__globals__
ns['m']=Emulator(rom,elf)
ns['m'].load(ns['out']/'gameplay.state')
(ns['out']/'results.json').unlink(missing_ok=True)
signal.alarm(900)
try:
    exec((ROOT/'tests/advanced_scenarios.py').read_text(),ns)
    (ns['out']/'results.json').write_text(json.dumps({'variant':variant,'rom_sha256':hashlib.sha256(pathlib.Path(rom).read_bytes()).hexdigest(),'passed':ns['passed'],'input_only':True,'checkpoints':'created by this exact ROM through controller input'},indent=2)+'\n')
finally:
    ns['m'].close()
