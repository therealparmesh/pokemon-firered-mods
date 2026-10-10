#!/usr/bin/env python3
"""Validate linked GBA header and complete ROM, without modifying it."""
import hashlib
import pathlib
import re
import sys
p = pathlib.Path(sys.argv[1])
b = p.read_bytes()
game = sys.argv[2]
expected = b'BPRE' if game == 'FIRERED' else b'BPGE'
assert 1024 * 1024 <= len(b) <= 32 * 1024 * 1024, f'{p}: invalid GBA ROM size {len(b)}'
assert b[0xAC:0xB0] == expected, f'{p}: wrong game code'
assert b[0xB2] == 0x96, f'{p}: missing GBA fixed byte'
assert b[0xBD] == (-sum(b[0xA0:0xBD]) - 0x19) & 255, f'{p}: invalid GBA header checksum'
# The logo must equal the linked upstream rom_header.s definition (known SHA-256).
assert hashlib.sha256(b[4:0xA0]).hexdigest() == '08a0153cfd6b0ea54b938f7d209933fa849da0d56f5a34c481060c9ff2fad818', f'{p}: invalid Nintendo logo'
baseline = len(sys.argv)>3 and sys.argv[3]=='1'
assert (b'FRLG_NATIVE_MODS_V1' in b) != baseline, f'{p}: native mod build marker mismatch'
if not baseline:
    # Use the game's character map to check visible text in the linked ROM.
    charmap = pathlib.Path(__file__).resolve().parent.parent / 'charmap.txt'
    characters = {m.group(1)[-1]: int(m.group(2), 16)
                  for line in charmap.read_text().splitlines()
                  if (m := re.fullmatch(r"'(\\?.)'\s*=\s*([0-9A-F]{2})", line))}
    for text in ['MODS / Main$', 'Disable all mods$', "Let's go, but play fair!$"]:
        assert bytes(characters[c] for c in text) in b, f'{p}: missing native text: {text}'
print(f'{p}: header/size OK; SHA-256 {hashlib.sha256(b).hexdigest()}')
