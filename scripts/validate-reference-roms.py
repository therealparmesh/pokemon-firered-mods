#!/usr/bin/env python3
"""Optional, user-provided English rev-0 reference dumps; never download them."""
import hashlib, pathlib, sys
root=pathlib.Path(__file__).resolve().parent.parent
missing=[]
for label,variant in [('FireRed','firered'),('LeafGreen','leafgreen')]:
    p=root/'roms'/(label+'.gba')
    if not p.exists():missing.append(str(p));continue
    expected=(root/(variant+'.sha1')).read_text().split()[0]
    actual=hashlib.sha1(p.read_bytes()).hexdigest()
    if actual!=expected:
        sys.exit(f'{p}: wrong identity ({actual}). Expected English revision 0 SHA-1 {expected}.')
    print(f'{p}: identity verified')
if missing:sys.exit('Missing optional references: '+', '.join(missing)+'. These are not required to build.')
