import hashlib, json, pathlib
root=pathlib.Path(__file__).resolve().parent.parent
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'dist').glob('*.gba')}
source_hash=hashlib.sha256()
for p in sorted(list((root/'src').rglob('*')) + list((root/'include').rglob('*'))):
    if p.is_file():
        source_hash.update(str(p.relative_to(root)).encode()); source_hash.update(p.read_bytes())
(root/'dist'/'manifest.json').write_text(json.dumps({'roms':files, 'source_sha256':source_hash.hexdigest(), 'upstream':(root/'config/dependencies.env').read_text(), 'toolchain':(root/'.build-deps/toolchain.txt').read_text()},indent=2)+'\n')
