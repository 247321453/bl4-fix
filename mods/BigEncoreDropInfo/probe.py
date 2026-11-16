# -*- coding: utf-8 -*-
"""Explicit synchronous key/console capture only. No hooks, workers, or writes to UObjects."""
import json
from itertools import islice, chain
from pathlib import Path
from datetime import datetime, timezone
import unrealsdk as sdk
from mods_base import get_pc

CLASSES = (
    '/Script/OakGame.OakUIScript_BigMap',
    '/Script/OakGame.OakUIDataCollector_BigMap',
    '/Script/OakGame.OakBossFight',
    '/Script/OakGame.OakInteractiveObject',
    '/Script/GbxUICoherent.GbxUIScript',
    '/Script/CohtmlPlugin.CohtmlBaseComponent',
    '/Script/CohtmlPlugin.CohtmlWidget',
    '/Script/UMG.WidgetComponent',
    '/Script/OakGame.OakUIDataCollector_InteractPrompt',
    '/Script/OakGame.StructuredInteractableUserState',
    '/Game/InteractiveObjects/GameSystemMachines/BossReplay/Script_BossReplay.Script_BossReplay_C',
)
TERMS = ('boss', 'replay', 'map', 'poi', 'hover', 'select', 'location', 'title',
         'description', 'data', 'model', 'view', 'widget', 'interact', 'usable',
         'script', 'name', 'context', 'definition', 'instance', 'consumer', 'target', 'current', 'prompt', 'text')


def destination():
    for parent in Path(__file__).parents:
        if parent.name.lower() == 'sdk_mods':
            return parent / 'settings' / 'BigEncoreDropInfo'
    raise RuntimeError('sdk_mods directory not found')


def field_schema(field, depth=0):
    kind = type(field).__name__
    row = {'name': str(field.Name), 'type': kind}
    if kind == 'UFunction':
        row['path'] = field._path_name()
        row['parameters'] = [field_schema(p, 3) for p in islice(field._properties(), 48)
                             if int(p.PropertyFlags) & 0x80]
    elif kind == 'ZStructProperty':
        row['struct'] = field.Struct._path_name()
        if depth < 2:
            row['fields'] = [field_schema(p, depth + 1) for p in islice(field.Struct._properties(), 64)]
    elif kind == 'ZArrayProperty' and depth < 2:
        row['inner'] = field_schema(field.Inner, depth + 1)
    elif kind in ('ZObjectProperty', 'ZWeakObjectProperty'):
        row['class'] = field.PropertyClass._path_name()
    return row


def schema(cls):
    result = []; seen = set()
    for f in chain(islice(cls._properties(), 512), islice(cls._fields(), 512)):
        identity = (str(f.Name), type(f).__name__)
        if identity in seen:
            continue
        seen.add(identity)
        try:
            result.append(field_schema(f))
        except Exception as exc:
            result.append({'name': identity[0], 'error': str(exc)[:200]})
    return result


def value(v, depth=0):
    if v is None or type(v) in (str, int, float, bool):
        return v[:1500] if isinstance(v, str) else v
    if hasattr(v, 'Class'):
        row = {'path': v._path_name(), 'class': v.Class._path_name()}
        if depth < 2:
            row['values'] = values(v, v.Class, depth + 1)
        return row
    if type(v).__name__ == 'WrappedStruct' and depth < 3:
        return values(v, v._type, depth + 1)
    if type(v).__name__ == 'WrappedArray' and depth < 3:
        return [value(x, depth + 1) for x in islice(v, 24)]
    return str(v)[:1500]


def values(obj, cls, depth=0):
    result = {}
    for f in islice(cls._properties(), 256):
        name = str(f.Name)
        if not any(t in name.lower() for t in TERMS):
            continue
        try:
            result[name] = value(getattr(obj, name), depth)
        except Exception as exc:
            result[name] = {'error': str(exc)[:160]}
    return result


def capture():
    # Invoked exclusively by native input/console callback on GameThread.
    root = destination(); root.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    path = root / ('capture-' + now.strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    report = {'version': '0.0.2', 'time_utc': now.isoformat(), 'read_only': True,
              'stage': 'started', 'classes': {}, 'objects': [], 'errors': []}
    def save(stage):
        report['stage'] = stage
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    save('started')
    try:
        pc = get_pc()
        if pc is not None:
            report['player'] = value(pc)
    except Exception as exc:
        report['errors'].append({'player': str(exc)[:300]})
    for name in ('/Script/OakGame.OakWidgetData_BigMap_POIData',):
        try:
            report['classes'][name] = schema(sdk.find_object('ScriptStruct', name))
        except Exception as exc:
            report['errors'].append({'struct': name, 'error': str(exc)[:300]})
    for name in CLASSES:
        save('class:' + name)
        try:
            cls = sdk.find_class(name)
            report['classes'][name] = schema(cls)
            # One enumeration per class per explicit capture, never per frame.
            # Cap reads and record truncation. Do not load absent blueprint assets.
            count = 0
            for obj in islice(sdk.find_all(cls, exact=False), 129):
                count += 1
                if count > 128:
                    report['errors'].append({'class': name, 'truncated': True})
                    break
                obj_path = obj._path_name()
                if 'Default__' in obj_path or obj_path.startswith('/Script/'):
                    continue
                if name.endswith('OakInteractiveObject'):
                    # Only read script references to select BossReplay instances.
                    try:
                        instances = obj.ScriptData.Instances
                        if not any('Script_BossReplay_C' in x.Class._path_name()
                                   for x in islice(instances, 16) if x is not None):
                            continue
                    except Exception:
                        continue
                report['objects'].append(value(obj))
        except Exception as exc:
            report['errors'].append({'class': name, 'error': str(exc)[:300]})
    save('complete')
    return path
