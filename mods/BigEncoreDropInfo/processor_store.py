# -*- coding: utf-8 -*-
"""Explicit user-recorded processor destinations; plain JSON only."""
import json
import os
from datetime import datetime, timezone
from .encore_policy import vector

TARGETS = {
    'processor_grasslands': ('Fadefields', 'world_p', 'grasslands', 'elpis'),
    'processor_shatteredlands': ('Carcadia Burn', 'world_p', 'shatteredlands', 'elpis'),
    'processor_mountains': ('Terminus Range', 'world_p', 'mountains', 'banjo'),
    'processor_cello': ("The Demon's Domain", 'cello_p', 'cello', 'banjo'),
}


def validate(key, record):
    if key not in TARGETS or not isinstance(record, dict):
        raise ValueError('Unknown processor target')
    if record.get('map_name') != TARGETS[key][1] or record.get('region_key') != TARGETS[key][2]:
        raise ValueError('Processor map/region mismatch')
    vector(record['position']); vector(record['rotation'])
    return record


def read(root):
    path = root / 'processor-positions.json'
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf8'))
    if data.get('schema') != 1:
        raise ValueError('Unsupported processor position schema')
    return {key: validate(key, row) for key, row in data['positions'].items()}


def save(root, key, record):
    validate(key, record)
    rows = read(root)
    rows[key] = record
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'processor-positions.json'
    if path.exists():
        # Keep the preceding complete recording for an accidental overwrite.
        backup = root / 'processor-positions.previous.json'
        backup.write_bytes(path.read_bytes())
    temporary = root / 'processor-positions.tmp'
    with temporary.open('w', encoding='utf8') as stream:
        json.dump({'schema': 1, 'positions': rows}, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return rows


def recording(key, position, rotation):
    _, world, region, _ = TARGETS[key]
    return validate(key, {'map_name': world, 'region_key': region,
        'position': list(vector(position)), 'rotation': list(vector(rotation)),
        'saved_at': datetime.now(timezone.utc).isoformat(),
        'source': 'user_F10_ground_anchor'})
