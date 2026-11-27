"""Validate the embedded glTF without Blender or third-party packages."""
import base64
import json
from pathlib import Path
import re
import struct

html = (Path(__file__).resolve().parents[1] / 'index.html').read_text()
raw = base64.b64decode(re.search(r"const MODEL_BASE64 = '([^']+)'", html)[1])
assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw))
length = struct.unpack_from('<I', raw, 12)[0]
gltf = json.loads(raw[20:20 + length])
assert any(n.get('extras', {}).get('walk_ceiling') for n in gltf['nodes'])
assert sum(bool(n.get('extras', {}).get('door_finish')) for n in gltf['nodes']) == 5
finishes = {re.match(r'I601_Paint_([^_]+)_(north|east|south|west)_', m.get('name', '')).groups()
            for m in gltf['materials'] if m.get('name', '').startswith('I601_Paint_')}
for room in ('master', 'small', 'drawing', 'kitchen', 'dining', 'ensuite', 'bathroom', 'wash'):
    assert any(key[0] == room for key in finishes), room
for room in ('master', 'small'):
    assert {side for key, side in finishes if key == room} == {'north', 'east', 'south', 'west'}

pieces = {n['name'].removeprefix('FURN_'): n for n in gltf['nodes'] if n.get('extras', {}).get('furniture')}
for size in ('small', 'master'):
    cupboard, loft = pieces['cupboard_' + size], pieces['loft_' + size]
    assert abs(cupboard['extras']['size_mm'][1] - loft['extras']['size_mm'][1]) < 0.01, size
    # The exporter rotates Blender Y to glTF -Z. Their centres must align too.
    assert abs(cupboard['translation'][2] - loft['translation'][2]) < 1e-6, size
    for index in loft['children']:
        node = gltf['nodes'][index]
        if 'mesh' not in node:
            continue
        for primitive in gltf['meshes'][node['mesh']]['primitives']:
            accessor = gltf['accessors'][primitive['attributes']['POSITION']]
            centre = loft['translation'][2] + node.get('translation', [0, 0, 0])[2]
            low, high = centre + accessor['min'][2], centre + accessor['max'][2]
            half = cupboard['extras']['size_mm'][1] / 2000
            assert low >= cupboard['translation'][2] - half - 1e-5
            assert high <= cupboard['translation'][2] + half + 1e-5
print(f'PASS: {len(finishes)} room/wall finishes; both loft bounds match cupboards')
