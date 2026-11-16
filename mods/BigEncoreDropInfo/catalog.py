# -*- coding: utf-8 -*-
"""Shared map/world presentation data; no Unreal imports or runtime pool traversal."""
import json
from importlib.resources import files
from html import escape
from .i18n import localize


def load():
    data = json.loads(files(__package__).joinpath('catalog.json').read_text(encoding='utf-8'))
    if data['schema'] != 1:
        raise ValueError('Unsupported catalog schema')
    for row in data['bosses'].values():
        row['drops'].sort(key=lambda drop: drop.get('rarity') != 'pearl')
    return data['bosses']


def processor_details(catalog):
    """Five activity variants share one dedicated pool; tutorial stays separate."""
    row=catalog.get('ordonite_pgg_activity',{})
    ko=any(0xAC00<=ord(c)<=0xD7A3 for c in row.get('name',''))
    aliases=row.get('map_names',[])
    names=aliases[0::2] if ko else aliases[1::2]
    return {'name':'Ordonite Processors' if ko else 'Ordonite Processor',
        'boss_names':names,
        'note':'Dedicated drops shared by the possible activity bosses.' if ko else 'Dedicated drops shared by the possible activity bosses.',
        'map_names':['Ordonite Processors','Ordonite Up!','Ordonite Processor','Ordonite Up!'],
        'world_keys':[],'station_ids':[],
        'drops':[{field:d.get(field,'') for field in ('name','kind','kind_label','rarity')}
            for d in row.get('drops',[]) if d.get('rarity') in ('legendary','pearl')]}


def resolve(catalog, *, station_id=None, boss_path=None):
    # Exact identifiers only. Boss name substrings cannot identify a station.
    matches = [key for key, row in catalog.items()
               if (station_id is not None and station_id in row['station_ids'])
               or (boss_path is not None and boss_path in row['boss_paths'])]
    return matches[0] if len(matches) == 1 else None


def text(catalog, boss_id, *, world=False):
    row = catalog.get(boss_id)
    if row is None:
        return ''
    display = localize(row)
    names = list(dict.fromkeys(d.get('cn_name') or d['name'] for d in display['drops']))
    header = ((display.get('cn_name') or row['name']) + '\n') if world else ''
    return header + '\n'.join('• ' + name for name in names)


def markup(catalog, boss_id, *, world=False):
    return escape(text(catalog, boss_id, world=world)).replace('\n', '<br>')
