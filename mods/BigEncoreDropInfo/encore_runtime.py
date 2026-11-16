# -*- coding: utf-8 -*-
"""Regional Encore discovery, native map travel and guarded destination streaming on GameThread.

HTTP workers only call snapshot/enqueue. No worker may dereference a UObject.
All cached UObject references are weak. A failed ABI/state check fails closed.
"""
import json
import re
import time
import uuid
from itertools import islice
from importlib.resources import files
from threading import Lock, get_ident
import unrealsdk as sdk
from unrealsdk.unreal import WeakPointer
from mods_base import get_pc
from .catalog import load, processor_details
from .probe import destination, schema
from .encore_policy import REGIONS, region_key, station_region, vector, candidates, landing, Requests
from . import encore_stream
from .native_call import named
from . import processor_store
from .i18n import localize, translate

SCRIPT = '/Game/InteractiveObjects/GameSystemMachines/BossReplay/Script_BossReplay.Script_BossReplay_C'
IDENT = 'LootMap.EncoreTeleport.v1'
_lock = Lock()
_gate = Requests()
_hooks = []
_active = False
_scan = False
_thread = None
_stations = {}
_catalog = {}
_locations = {}
_routes = {}
_health = {}
_waypoints = {}
_processor_target = None
_record_requested = False
_processor_notice = ''
_journey = None
_last_result = None
_world = None
_player = None
_region = None
_region_world = None
_last_move = 0.
_busy = False
_schema_written = False
_lifecycle_ready = False
_defer_after = 0.
_state = {'status': 'closed', 'bosses': []}


def log(**fields):
    sdk.logging.info('[BigEncoreMapTeleport] ' + json.dumps(fields, ensure_ascii=False))
    try:
        root = destination(); root.mkdir(parents=True, exist_ok=True)
        (root/'encore-latest.json').write_text(json.dumps(fields, ensure_ascii=False, indent=2), encoding='utf8')
    except OSError:
        pass


def checked(obj):
    if obj is None:
        raise RuntimeError('Object unavailable')
    obj = WeakPointer(obj)()
    if obj is None:
        raise RuntimeError('Object expired')
    valid=signature(static_library(),'IsValid',{'object':'ObjectProperty','returnvalue':'BoolProperty'})
    if not boolean(valid(Object=obj),'IsValid'):
        raise RuntimeError('Engine IsValid rejected object')
    if 'Default__' in obj._path_name():
        raise RuntimeError('Default object is not a live target')
    # WeakPointer resolves through the engine object serial; do not retain raw addresses.
    if hasattr(obj, 'bActorIsBeingDestroyed') and obj.bActorIsBeingDestroyed:
        raise RuntimeError('Actor is being destroyed')
    return obj


def world_of(actor):
    actor = checked(actor)
    level = checked(actor.Outer)
    world = checked(level.OwningWorld)
    if world.Class._path_name() != '/Script/Engine.World':
        raise RuntimeError('World not available')
    return world


def signature(obj, name, expected):
    fn = obj.Class._find(name)
    if type(fn).__name__ != 'UFunction':
        raise RuntimeError(name + ': unavailable native function')
    actual = {str(p.Name).casefold(): type(p).__name__.removeprefix('Z')
              for p in fn._properties() if int(p.PropertyFlags)&0x80}
    if actual != expected:
        raise RuntimeError(name + ': unsupported signature ' + str(actual))
    structs={}
    if name in ('K2_GetActorLocation','K2_GetActorRotation'):
        structs['returnvalue']='/Script/CoreUObject.'+('Vector' if name.endswith('Location') else 'Rotator')
    if name=='K2_TeleportTo':
        structs={'destlocation':'/Script/CoreUObject.Vector','destrotation':'/Script/CoreUObject.Rotator'}
    if name in ('LineTraceSingle','CapsuleTraceSingle'):
        structs={'start':'/Script/CoreUObject.Vector','end':'/Script/CoreUObject.Vector',
            'outhit':'/Script/Engine.HitResult','tracecolor':'/Script/CoreUObject.LinearColor',
            'tracehitcolor':'/Script/CoreUObject.LinearColor'}
    for prop in fn._properties():
        key=str(prop.Name).casefold()
        if key in structs and prop.Struct._path_name()!=structs[key]:
            raise RuntimeError(name+': unexpected struct '+key)
    return named(getattr(obj,name),(p for p in fn._properties() if int(p.PropertyFlags)&0x80))


def bool_call(obj, name):
    return boolean(signature(obj, name, {'returnvalue':'BoolProperty'})(),name)


def boolean(result,name):
    # A tuple containing False is truthy in Python; never treat it as success.
    if type(result) is bool:
        return result
    if isinstance(result,tuple) and result and type(result[0]) is bool:
        return result[0]
    raise RuntimeError(name+': unexpected Boolean return ABI')


def trace_result(result):
    # Const-reference arguments can also appear among SDK out values. Locate the
    # uniquely typed HitResult instead of assuming a two-element tuple.
    values=list(result) if isinstance(result,tuple) else []
    shape=[];hits=[]
    for value in values[:16]:
        kind=type(value).__name__
        try:
            path=value._type._path_name()
        except AttributeError:
            path=None
        shape.append({'type':kind,'struct':path})
        if path=='/Script/Engine.HitResult':
            hits.append(value)
    try:
        root=destination();root.mkdir(parents=True,exist_ok=True)
        (root/'encore-trace-abi.json').write_text(json.dumps({'return_type':type(result).__name__,'values':shape},indent=2),encoding='utf8')
    except OSError:
        pass
    if not values or type(values[0]) is not bool or len(values)>16 or len(hits)!=1:
        raise RuntimeError('Unexpected trace output ABI: '+str(shape)[:500])
    return values[0],hits[0]


def vec(v):
    return vector((v.X, v.Y, v.Z))


def native_vec(v):
    x,y,z = vector(v)
    return sdk.make_struct('/Script/CoreUObject.Vector', X=x, Y=y, Z=z)


def map_name(world):
    return world._path_name().split(':',1)[0].rsplit('.',1)[-1].casefold()


def contexts():
    pc = checked(get_pc())
    pawn = checked(pc.Pawn)
    world = world_of(pawn)
    if world_of(pc) != world:
        raise RuntimeError('Controller world changed')
    return pc,pawn,world


def validate_player(pc, pawn, world, *, allow_rebind=False):
    if not bool_call(pc, 'IsLocalPlayerController') or not bool_call(pawn, 'HasAuthority'):
        raise RuntimeError('Host / single-player only')
    if not allow_rebind and (_world is None or _world() != world or _player is None or _player() != pawn):
        raise RuntimeError('World or player changed; reopen map')
    ps = checked(pc.PlayerState)
    if bool(ps.bDrivingVehicle) or not pawn.Class._inherits(sdk.find_class('/Script/Engine.Character')):
        raise RuntimeError('Exit your vehicle first')
    if bool_call(pawn, 'IsDead') or not bool_call(pawn, 'IsHealthy'):
        raise RuntimeError('Dead / respawning / fight for your life')
    if pc.CurrentTransitionZone is not None or bool(ps.bInZoneTransition):
        raise RuntimeError('Zone transition in progress')
    status = pc.TravelStatus
    if status.bDisallowLocalTravel or status.bIsTravelingToMainMenu:
        raise RuntimeError('Travel is currently blocked')
    # Require symbolic idle status; an unknown enum is never interpreted as idle.
    label = str(getattr(status.status,'name',status.status)).split('.')[-1].split(':')[0].strip(' <>').casefold()
    if label not in ('none', 'idle', 'nottraveling', 'nottravelling', 'inactive'):
        raise RuntimeError('Travel status is not known idle: ' + str(status.status))
    if int(pc.SeamlessTravelCount) != int(pc.LastCompletedSeamlessTravelCount):
        raise RuntimeError('Seamless loading in progress')
    if int(pc.ActiveCinematicModeIdent.TokenCount) != 0:
        raise RuntimeError('Cinematic in progress')
    move = checked(pawn.CharacterMovement)
    # Walking/nav-walking only: avoids midair/swimming/flying/vehicle transitions.
    if int(move.MovementMode) not in (1,2):
        raise RuntimeError('Player must be standing on the ground')
    return move


def def_name(value):
    # Read identifiers without stringifying a potentially huge resolved Nexus row.
    try:
        return str(value._name).casefold()
    except AttributeError:
        if type(value).__name__ == 'WrappedStruct':
            try:
                count=int(value.TokenCount)
                if count==0:
                    return ''
                tokens=[str(value.InlineTokens.Name)]
                if count>1:
                    tokens.extend(str(t.Name) for t in islice(value.ExternalTokens,8))
                return '_'.join(tokens).casefold()
            except AttributeError:
                pass
        match = re.search(r"(?:FGbxDefPtr|FGameDataHandle)\([^']*'([^']+)'", str(value)[:300])
        return match[1].casefold() if match else ''


def current_region(pc, world):
    name = map_name(world)
    if name != 'world_p':
        return region_key(name) or name
    if _region_world is not None and _region_world() == world:
        if _region:
            return _region
    # Some native region updates bypass reflected RPC hooks. Query only actual
    # region/zone volumes overlapping the pawn; never infer from camera/checkpoint.
    try:
        pawn=checked(pc.Pawn)
        result=signature(pawn,'GetOverlappingActors',{'overlappingactors':'ArrayProperty','classfilter':'ClassProperty'})(OverlappingActors=[],ClassFilter=None)
        # The installed SDK includes Ellipsis (void return) before out params.
        if not isinstance(result,tuple) or len(result)!=2 or result[0] is not Ellipsis:
            return None
        overlaps=list(islice(result[1],129))
        if len(overlaps)>128:
            return None
        regions=set();observed=[]
        for actor in overlaps:
            actor=checked(actor)
            if world_of(actor)!=world:
                continue
            class_name=actor.Class._path_name()
            if not any(t in class_name.casefold() for t in ('region','zone','volume')):
                continue
            fields={}
            for prop in islice(actor.Class._properties(),160):
                key=str(prop.Name)
                if key.casefold() not in ('region','regiondef','worldregion','regionname','worldregiondef','discoveryregion'):
                    continue
                value=def_name(getattr(actor,key));fields[key]=value
                region=region_key(value)
                if region:
                    regions.add(region)
            if len(observed)<16:
                observed.append({'class':class_name,'actor':actor._path_name(),'region_fields':fields})
        root=destination();root.mkdir(parents=True,exist_ok=True)
        (root/'encore-region-overlaps.json').write_text(json.dumps({'map':name,'candidates':observed,'regions':sorted(regions)},ensure_ascii=False,indent=2),encoding='utf8')
        if len(regions)==1:
            return next(iter(regions))
    except Exception:
        pass
    return None


def station_match(actor, script):
    station = def_name(actor.OakDiscoveryLocationConfig.LocationDisplayData)
    keys = [k for k,r in _catalog.items() if station in r['station_ids']]
    if len(keys) != 1:
        display = def_name(script.BossDisplayName)
        keys = [k for k,r in _catalog.items() if r['station_ids'] and display in r['world_keys']]
    return (keys[0],station) if len(keys)==1 else (None,station)


def capture_schema(pc, pawn, world):
    """Bounded first diagnostic, reflected definitions only; no writes to game."""
    global _schema_written
    if _schema_written:
        return
    root = destination(); root.mkdir(parents=True, exist_ok=True)
    report = {'version':'0.6.0-preview.12', 'classes':{}, 'state':{}}
    objects = [pc, pawn, world, pc.PlayerState, pawn.CharacterMovement, pawn.CapsuleComponent]
    for obj in objects:
        if obj is not None:
            report['classes'][obj.Class._path_name()] = schema(obj.Class)
    for field in ('TravelStatus','ActiveCinematicModeIdent','StateName'):
        report['state'][field] = str(getattr(pc, field, None))[:800]
    for name in ('/Script/Engine.KismetSystemLibrary','/Script/Engine.KismetMathLibrary',
            '/Script/Engine.GameplayStatics','/Script/Engine.TargetPoint','/Script/Engine.WorldPartitionStreamingSourceComponent'):
        try:
            report['classes'][name]=schema(sdk.find_class(name))
        except Exception as exc:
            report['classes'][name]={'error':str(exc)[:200]}
    (root/'encore-native-schema.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    _schema_written = True


def loaded_scripts():
    """An unloaded Blueprint is absence of live machines, not a broken catalog.

    Do not cache a missing class or force-load it. Destination streaming can load
    it later, so resolve it afresh on discovery and after destination loading.
    """
    try:
        cls=sdk.find_class(SCRIPT)
    except ValueError:
        return []
    if cls is None:
        return []
    scripts=list(islice(sdk.find_all(cls,exact=True),257))
    if len(scripts)>256:
        raise RuntimeError('Encore discovery limit exceeded')
    return scripts


def discover():
    global _world,_player,_stations,_state
    report = {'status':'unavailable','bosses':[], 'map_session':_gate.token}
    try:
        pc,pawn,world = contexts()
        _world, _player = WeakPointer(world), WeakPointer(pawn)
        name = map_name(world); region = current_region(pc, world)
        report.update(current_map=name,current_region=REGIONS.get(region,region),region_key=region)
        # Capture before state checks: an unsupported build has a useful diagnosis.
        capture_schema(pc,pawn,world)
        validate_player(pc,pawn,world)
        found = {}; scripts=loaded_scripts()
        for script in scripts:
            try:
                script=checked(script); actor=checked(script.Outer)
                if world_of(actor)!=world or actor.bHidden:
                    continue
                key,station=station_match(actor,script)
                if key is None:
                    continue
                r=station_region(station)
                # All regions are listed; UWorld identity still guards live actors.
                location=vec(signature(actor,'K2_GetActorLocation',{'returnvalue':'StructProperty'})())
                rotation=signature(actor,'K2_GetActorRotation',{'returnvalue':'StructProperty'})()
                found.setdefault(key,[]).append({'actor':WeakPointer(actor),'script':WeakPointer(script),
                    'station_id':station,'location':location,'actor_path':actor._path_name(),
                    'rotation':vector((rotation.pitch,rotation.yaw,rotation.roll))})
            except (AttributeError,TypeError,ValueError,RuntimeError):
                continue
        # Ambiguous duplicate actors are omitted; never choose the first one.
        _stations={k:v[0] for k,v in found.items() if len(v)==1}
        rows=[{'id':k,'name':_catalog[k]['name'],'map_name':name,'world_name':world._path_name(),
               'station_id':v['station_id'],'source':'runtime_actor',
               'region_key':station_region(v['station_id']) or region or name,
               'region_name':REGIONS.get(station_region(v['station_id']),REGIONS.get(region,region or name)),
               'encore_station_actor':v['actor_path'],
               'encore_station_transform':{'location':v['location'],'rotation':v['rotation']},
               'fallback_position':None,'fallback_rotation':None} for k,v in _stations.items()]
        by_key={r['id']:r for r in rows}
        for station_id,location in _locations.items():
            key=location['boss_id']
            if key not in _catalog:
                continue
            same_map=location['map_name']==name
            if key not in _stations:
                _stations[key]={'static':location,'station_id':station_id}
            row=by_key.get(key)
            if row is None:
                row={'id':key,'name':_catalog[key]['name'],'station_id':station_id,
                    'map_name':location['map_name'],'world_name':location['world_name'],
                    'source':'official_map_metadata','region_key':location['region_key'],
                    'region_name':location['region_name_en'],
                    'region_name_ko':location['region_name_ko'],
                    'encore_station_actor':location['actor_name'],
                    'encore_station_transform':None}
                rows.append(row)
            else:
                row['region_key']=location['region_key']
                row['region_name']=location['region_name_en']
                row['region_name_ko']=location['region_name_ko']
            row.update(fallback_position=location['position'],fallback_rotation=location['rotation'],
                same_map=same_map,travel_available=True,cross_map=not same_map,
                unavailable_reason=None)
        for row in rows:
            row['health']={**_health.get(row['id'],{})}
            row['drops']=[{'name':d['name'],'rarity':d.get('rarity','legendary'),
                'kind':d.get('kind',''),'kind_label':d.get('kind_label','')}
                for d in _catalog[row['id']].get('drops',[])]
            override=entrance_destination(row['id'])
            if override is not None:
                row['destination_note']=override['destination_note']
        report.update(status='ready',bosses=sorted(rows,key=lambda r:(r['region_name'],r['name'])),
            waypoints=[{**w,'cross_map':w['map_name']!=name,
                'drops':[{field:d.get(field,'') for field in ('name','kind','kind_label','rarity')}
                    for d in _catalog.get(w.get('drop_catalog_id'),{}).get('drops',[])]}
                for w in _waypoints.values() if w['kind']=='native_waypoint'],
            scope='all_catalog_regions',
            region_detection='native_player_region' if region else 'unavailable_no_region_claim')
        log(**{'Current Map':name,'Current Region':region,'Encore Boss Count':len(rows)})
    except Exception as exc:
        _stations={}; report['reason']=str(exc)[:400]
        log(**{'Teleport Failed Reason':report['reason']})
    with _lock:
        _state=report


def static_library():
    obj=sdk.find_object('Object','/Script/Engine.Default__KismetSystemLibrary')
    if obj is None or WeakPointer(obj)() is None or obj.Class._path_name()!='/Script/Engine.KismetSystemLibrary':
        raise RuntimeError('Kismet system library unavailable')
    return obj


def _trace_target(system,pc,pawn,actor,location,yaw,radius,height,*,saved_point=False):
    attempts=[]
    def save():
        try:
            root=destination();root.mkdir(parents=True,exist_ok=True)
            (root/'encore-ground-traces.json').write_text(json.dumps({'station_position':list(location),'attempts':attempts},indent=2),encoding='utf8')
        except OSError:
            pass
    line=signature(system,'LineTraceSingle',{
        'worldcontextobject':'ObjectProperty','start':'StructProperty','end':'StructProperty',
        'tracechannel':'ByteProperty','btracecomplex':'BoolProperty','actorstoignore':'ArrayProperty',
        'drawdebugtype':'ByteProperty','outhit':'StructProperty','bignoreself':'BoolProperty',
        'tracecolor':'StructProperty','tracehitcolor':'StructProperty','drawtime':'FloatProperty',
        'returnvalue':'BoolProperty'})
    cap=signature(system,'CapsuleTraceSingle',{
        'worldcontextobject':'ObjectProperty','start':'StructProperty','end':'StructProperty',
        'radius':'FloatProperty','halfheight':'FloatProperty','tracechannel':'ByteProperty',
        'btracecomplex':'BoolProperty','actorstoignore':'ArrayProperty','drawdebugtype':'ByteProperty',
        'outhit':'StructProperty','bignoreself':'BoolProperty','tracecolor':'StructProperty',
        'tracehitcolor':'StructProperty','drawtime':'FloatProperty','returnvalue':'BoolProperty'})
    black=sdk.make_struct('/Script/CoreUObject.LinearColor',R=0.,G=0.,B=0.,A=1.)
    common=dict(WorldContextObject=pawn,TraceChannel=0,bTraceComplex=False,ActorsToIgnore=[pawn],
        DrawDebugType=0,OutHit=sdk.make_struct('/Script/Engine.HitResult'),bIgnoreSelf=True,
        TraceColor=black,TraceHitColor=black,DrawTime=0.)
    points = ([location, (location[0]+80,location[1],location[2]),
        (location[0]-80,location[1],location[2]), (location[0],location[1]+80,location[2]),
        (location[0],location[1]-80,location[2])] if saved_point else candidates(location,yaw))
    for point in points:
        x,y,z=point
        result=line(Start=native_vec((x,y,z+250)),End=native_vec((x,y,z-250)),**common)
        ok,hit=trace_result(result)
        attempt={'candidate':list(point),'floor_hit':ok};attempts.append(attempt)
        if not ok:
            continue
        try:
            dest=landing({'point':vec(hit.ImpactPoint),'normal':vec(hit.ImpactNormal),
                'blocking':bool(hit.bBlockingHit),'penetrating':bool(hit.bStartPenetrating)},point,radius,height)
        except ValueError as exc:
            attempt['rejected']=str(exc)
            continue
        # Full player capsule clearance. Do not ignore station/walls/other players.
        result=cap(Start=native_vec(dest),End=native_vec((dest[0],dest[1],dest[2]+1)),
            Radius=radius+3,HalfHeight=height,**common)
        blocked,clearance=trace_result(result)
        attempt['capsule_blocked']=blocked;attempt['penetrating']=bool(clearance.bStartPenetrating)
        if blocked or clearance.bStartPenetrating:
            continue
        attempt['landing']=list(dest);save()
        return dest, (yaw if saved_point else ((yaw+180)%360))
    save()
    raise RuntimeError('No safe walkable position in front of station')


def teleport(key,token,sequence,*,journey=None,defer_unloaded=False):
    global _last_move,_busy,_last_result
    report={'Selected Boss':key,'Request Sequence':sequence,'Teleport Success':False}
    try:
        if journey is None and (not _active or token!=_gate.token or _busy or time.monotonic()-_last_move<3):
            raise RuntimeError('Map session expired or another teleport in progress')
        _busy=True
        record=journey['record'] if journey is not None else _stations.get(key)
        if record is None:
            raise RuntimeError('Station not present in this map session')
        entrance=entrance_destination(key)
        if entrance is not None:
            record={'static':entrance}
            report['Destination Kind']='boss_room_entrance'
        pc,pawn,world=contexts();validate_player(pc,pawn,world,allow_rebind=journey is not None)
        if journey is None and _state.get('region_key') is not None and current_region(pc,world)!=_state.get('region_key'):
            raise RuntimeError('Player region changed; reopen map')
        if 'static' in record:
            station=record['static']
            if station['map_name']!=map_name(world):
                raise RuntimeError('Enter destination map first: '+station['world_name'])
            # Official discovery metadata, never a nearest waypoint or boss center.
            # Collision must already be loaded here: traces below fail closed otherwise.
            actor=None;location=vector(station['position']);yaw=float(station['rotation'][1])
            actor_path=station['actor_name'];report['Position Source']=station.get('position_source','official_map_metadata')
        else:
            actor=checked(record['actor']());script=checked(record['script']())
            if world_of(actor)!=world or script.Outer!=actor or actor.bHidden:
                raise RuntimeError('Encore station unloaded')
            if station_match(actor,script)[0]!=key:
                raise RuntimeError('Encore station identity changed')
            location=vec(signature(actor,'K2_GetActorLocation',{'returnvalue':'StructProperty'})())
            rotation=signature(actor,'K2_GetActorRotation',{'returnvalue':'StructProperty'})()
            yaw=float(rotation.yaw);actor_path=actor._path_name();report['Position Source']='runtime_actor'
        capsule=checked(pawn.CapsuleComponent)
        radius=float(signature(capsule,'GetScaledCapsuleRadius',{'returnvalue':'FloatProperty'})())
        height=float(signature(capsule,'GetScaledCapsuleHalfHeight',{'returnvalue':'FloatProperty'})())
        dest,yaw=_trace_target(static_library(),pc,pawn,actor,location,yaw,radius,height,
            saved_point='static' in record and record['static'].get('kind')=='saved_processor')
        function=signature(pawn,'K2_TeleportTo',{'destlocation':'StructProperty','destrotation':'StructProperty','returnvalue':'BoolProperty'})
        # Final recheck after traces, before the only movement call.
        validate_player(pc,pawn,world,allow_rebind=journey is not None)
        if journey is None and (not _active or token!=_gate.token):
            raise RuntimeError('Map closed during confirmation')
        _last_move=time.monotonic()
        success=boolean(function(DestLocation=native_vec(dest),
            DestRotation=sdk.make_struct('/Script/CoreUObject.Rotator',pitch=0.,yaw=yaw,roll=0.)),'K2_TeleportTo')
        report.update({'Encore Actor':actor_path,'Encore Position':list(dest),'Teleport Success':success})
        if not success:
            raise RuntimeError('Engine safe teleport rejected destination')
        # Do not change spawn checkpoint, boss state, velocity or activate the station.
    except Exception as exc:
        report['Teleport Failed Reason']=str(exc)[:400]
    finally:
        _busy=False
    if defer_unloaded and report.get('Teleport Failed Reason')=='No safe walkable position in front of station':
        return report
    with _lock:
        _state['result']=report
        _last_result=report
    log(**report)
    return report


def entrance_destination(key):
    """Explicit user-approved entrance, separate from the real Encore catalog."""
    entry=_routes.get(key,{}).get('arrival_override')
    if entry is None:
        return None
    choices=[r for r in _locations.values() if r['boss_id']==key]
    if len(choices)!=1 or entry.get('user_approved') is not True or entry.get('kind')!='boss_room_entrance' or entry.get('map_name')!=choices[0]['map_name']:
        raise RuntimeError('Invalid approved entrance destination')
    vector(entry['position']);vector(entry['rotation'])
    return {**choices[0],**entry,'position_source':'user_approved_official_entrance'}


def resolve_destination(key,world):
    if key in processor_store.TARGETS:
        point=_waypoints.get(key)
        if point is None or point['map_name']!=map_name(world):
            raise RuntimeError('Recorded processor destination unavailable')
        return {'static':point}
    entrance=entrance_destination(key)
    if entrance is not None:
        if entrance['map_name']!=map_name(world):
            raise RuntimeError('Exact entrance destination not found in this world')
        return {'static':entrance}
    matches=[]
    for script in loaded_scripts():
        try:
            script=checked(script);actor=checked(script.Outer)
            if world_of(actor)==world and not actor.bHidden and station_match(actor,script)[0]==key:
                matches.append({'actor':WeakPointer(actor),'script':WeakPointer(script)})
        except (AttributeError,RuntimeError,TypeError):
            continue
    if len(matches)>1:
        raise RuntimeError('Ambiguous loaded Encore station')
    if matches:
        return matches[0]
    choices=[(sid,r) for sid,r in _locations.items() if r['boss_id']==key and r['map_name']==map_name(world)]
    if len(choices)!=1:
        raise RuntimeError('Exact Encore destination not found in this world')
    sid,row=choices[0]
    return {'static':row,'station_id':sid}


def end_journey(reason=None):
    global _journey,_busy,_last_result
    job=_journey
    if job is None:
        return
    try:
        if job.get('lease') is not None:
            job['lease'].close()
    except Exception as exc:
        log(**{'Streaming Cleanup':str(exc)[:200]})
    if reason:
        report={'Selected Boss':job['key'],'Request Sequence':job['sequence'],
            'Teleport Success':False,'Teleport Failed Reason':reason}
        with _lock:
            _last_result=report;_state['result']=report
        log(**report)
    _journey=None;_busy=False


def start_journey(key,token,sequence):
    global _journey,_busy,_last_result,_last_move
    if _journey is not None or not _active or token!=_gate.token:
        raise RuntimeError('Another journey is running or map session expired')
    pc,pawn,world=contexts();validate_player(pc,pawn,world)
    choices=[_waypoints[key]] if key in _waypoints else [r for r in _locations.values() if r['boss_id']==key]
    if len(choices)!=1:
        raise RuntimeError('Exact machine metadata unavailable')
    target=entrance_destination(key) or choices[0];cross=target['map_name']!=map_name(world)
    job={'id':uuid.uuid4().hex,'key':key,'sequence':sequence,'token':token,
        'target':target,'source_map':map_name(world),'controller':WeakPointer(pc),
        'destination_kind':target.get('kind','encore_station'),
        'player_id':int(checked(pc.PlayerState).PlayerId),'cross_map':cross,
        'stage':'map_loading' if cross else 'destination_loading','stable':0,
        'next_poll':time.monotonic()+.25,'deadline':time.monotonic()+90,
        'lease':None,'cancel':False}
    _journey=job;_busy=True;_last_result=None
    with _lock:
        _state.pop('result',None)
    try:
        if cross or target.get('kind')=='native_waypoint':
            route=_waypoints.get(key) or _routes.get(key)
            if route is None or route['map_name']!=target['map_name']:
                raise RuntimeError('No native entry route for exact destination map')
            fn=signature(pc,'RequestTeleportToStation',{'station':'GameDataHandleProperty',
                'bforrespawn':'BoolProperty','blocalonly':'BoolProperty'})
            from unrealsdk.unreal import FGameDataHandle
            station=FGameDataHandle(24576,route['station'])
            _last_move=time.monotonic()
            fn(station=station,bForRespawn=False,bLocalOnly=False)
        log(**{'Selected Boss':key,'Travel Stage':job['stage'],'Destination Map':target['map_name'],
            'Native Entry Station':(_waypoints.get(key) or _routes.get(key,{})).get('station') if cross or target.get('kind')=='native_waypoint' else None})
    except Exception as exc:
        end_journey(str(exc)[:400])


def begin_travel(key,token,sequence):
    try:
        if key in _waypoints:
            start_journey(key,token,sequence)
            return
        pc,pawn,world=contexts()
        target=next((r for r in _locations.values() if r['boss_id']==key),None)
        if target and target['map_name']!=map_name(world):
            start_journey(key,token,sequence)
            return
        result=teleport(key,token,sequence,defer_unloaded=True)
        if result.get('Teleport Failed Reason')=='No safe walkable position in front of station':
            start_journey(key,token,sequence)
    except Exception as exc:
        report={'Selected Boss':key,'Request Sequence':sequence,'Teleport Success':False,
            'Teleport Failed Reason':str(exc)[:400]}
        global _last_result
        with _lock:
            _last_result=report;_state['result']=report
        log(**report)


def poll_journey():
    global _busy,_last_result
    job=_journey
    if job is None:
        return
    now=time.monotonic()
    if job.get('cancel'):
        end_journey('Travel cancelled by player');return
    if now>job['deadline']:
        end_journey('Destination loading timed out; native travel may be locked or unavailable');return
    if now<job['next_poll']:
        return
    job['next_poll']=now+.25
    if job['stage']=='arrival':
        end_journey();return
    try:
        pc,pawn,world=contexts()
    except (RuntimeError,AttributeError):
        return # Native map travel can temporarily remove the controller/pawn.
    try:
        if int(checked(pc.PlayerState).PlayerId)!=job['player_id']:
            raise RuntimeError('Local player identity changed during travel')
        try:
            validate_player(pc,pawn,world,allow_rebind=True)
        except RuntimeError as exc:
            if any(s in str(exc) for s in ('transition','loading','Travel status','currently blocked','ground')):
                job['stable']=0;return
            raise
        current=map_name(world)
        if current!=job['target']['map_name']:
            if job['stage']=='map_loading' and current==job['source_map']:
                return
            raise RuntimeError('Unexpected destination world during travel')
        if not job['cross_map'] and job['controller']()!=pc:
            raise RuntimeError('Controller changed during local travel')
        if job['stage']=='map_loading':
            job['stable']+=1
            if job['stable']<4:
                return
            job.update(stage='destination_loading',stable=0)
        if job.get('destination_kind')=='native_waypoint':
            position=vec(signature(pawn,'K2_GetActorLocation',{'returnvalue':'StructProperty'})())
            target=vector(job['target']['position'])
            if sum((a-b)**2 for a,b in zip(position,target))>1000.**2:
                job['stable']=0
                return
            job['stable']+=1
            if job['stable']<4:
                return
            report={'Selected Boss':job['key'],'Request Sequence':job['sequence'],'Teleport Success':True,
                'Destination Kind':'native_waypoint','Destination Name':job['target']['name'],
                'Position Source':'native_fast_travel','Encore Position':list(position)}
            with _lock:
                _last_result=report;_state['result']=report
            log(**report);job.update(stage='arrival',next_poll=now+2.)
            return
        if job['lease'] is None:
            job['lease']=encore_stream.create(pc,pawn,world,job['target']['position'],checked,bool_call,world_of)
            job.update(stable=0,stream_started=now,next_probe=now+4.,next_diagnostic=now+5.)
            log(**{'Selected Boss':job['key'],'Travel Stage':'destination_loading'})
            return
        ready=job['lease'].ready(world)
        job['stable']=job['stable']+1 if ready else 0
        # A partition completion flag covers streaming cells beyond the station.
        # It is advisory: exact destination ground/capsule traces remain the
        # authority. Probe at most once per second after a bounded warm-up even
        # when a distant/nested cell keeps the completion flag false (Elpis).
        if now>=job.get('next_diagnostic',float('inf')):
            log(**{'Selected Boss':job['key'],'Travel Stage':'destination_loading',
                'Streaming Complete':ready,'Encore Position':job['target']['position'],
                'Destination Wait Seconds':round(now-job['stream_started'],1)})
            job['next_diagnostic']=now+5.
        if job['stable']<4 and now<job.get('next_probe',float('inf')):
            return
        if now<job.get('last_probe',0)+1.:
            return
        job['last_probe']=now
        job['record']=resolve_destination(job['key'],world)
        result=teleport(job['key'],job['token'],job['sequence'],journey=job,defer_unloaded=True)
        _busy=True
        if result['Teleport Success']:
            job.update(stage='arrival',next_poll=now+2.)
        elif result.get('Teleport Failed Reason')=='No safe walkable position in front of station':
            job['next_poll']=now+1.
        else:
            end_journey(result.get('Teleport Failed Reason','Safe teleport failed'))
    except Exception as exc:
        end_journey(str(exc)[:400])


def processor_rows():
    details=processor_details(_catalog)
    return [{**details,'id':key,'name':label+' · Ordonite Processor','kind':'saved_processor',
        'region_key':column,'record_region':region,'recorded':key in _waypoints,
        'map_name':name} for key,(label,name,region,column) in processor_store.TARGETS.items()]


def install_processor_records(rows):
    for key,row in rows.items():
        processor_store.validate(key,row)
        label,name,region,_=processor_store.TARGETS[key]
        routes=[_routes[r['boss_id']] for r in _locations.values()
            if r['map_name']==name and r['region_key']==region and r['boss_id'] in _routes
            and _routes[r['boss_id']]['map_name']==name]
        if not routes:
            raise ValueError('No native map entry route for '+key)
        _waypoints[key]={**row,'id':key,'name':label+' · Ordonite Processor',
            'kind':'saved_processor','world_name':name,'actor_name':'user_recorded_processor',
            'station':routes[0]['station'],'position_source':'user_F10_ground_anchor'}


def request_processor_record():
    """Key callback only queues Python state; native reads run on GameThread."""
    global _record_requested
    with _lock:
        _record_requested=True


def record_processor():
    global _processor_notice
    try:
        key=_processor_target
        if key not in processor_store.TARGETS:
            raise RuntimeError('First select a processor for recording in the Big Encore list.')
        if _busy or _journey is not None:
            raise RuntimeError('Cannot record a position during travel.')
        pc,pawn,world=contexts();validate_player(pc,pawn,world,allow_rebind=True)
        label,name,region,_=processor_store.TARGETS[key]
        if map_name(world)!=name:
            raise RuntimeError('Enter the selected processor map before recording: '+label)
        observed=current_region(pc,world)
        if name=='world_p' and observed is not None and observed!=region:
            raise RuntimeError('Current region does not match the selected recording target: '+label)
        position=vec(signature(pawn,'K2_GetActorLocation',{'returnvalue':'StructProperty'})())
        rotation=signature(pawn,'K2_GetActorRotation',{'returnvalue':'StructProperty'})()
        capsule=checked(pawn.CapsuleComponent)
        radius=float(signature(capsule,'GetScaledCapsuleRadius',{'returnvalue':'FloatProperty'})())
        height=float(signature(capsule,'GetScaledCapsuleHalfHeight',{'returnvalue':'FloatProperty'})())
        # Save a floor anchor, not a character-dependent capsule centre.
        anchor=(position[0],position[1],position[2]-height)
        safe,yaw=_trace_target(static_library(),pc,pawn,None,anchor,float(rotation.yaw),radius,height,saved_point=True)
        row=processor_store.recording(key,(safe[0],safe[1],safe[2]-height-4.),(0.,yaw,0.))
        rows=processor_store.save(destination(),key,row)
        install_processor_records(rows)
        _processor_notice=label+' processor position saved (F10).'
        log(**{'Processor Saved':key,'Map':name,'Position':row['position'],'Recorder Notice':_processor_notice})
    except Exception as exc:
        _processor_notice='Position recording failed: '+str(exc)[:240]
        log(**{'Processor Save Failed':str(exc)[:240]})
    try:
        pc=checked(get_pc())
        signature(pc,'ClientMessage',{'s':'StrProperty','type':'NameProperty','msglifetime':'FloatProperty'})(
            S=translate(_processor_notice),type='None',MsgLifeTime=6.)
    except Exception:
        # HUD messaging is optional; the map status and disk log remain available.
        pass


def snapshot():
    with _lock:
        result=dict(_state)
        result['processor_notice']=_processor_notice
        result['processors']=processor_rows()
        if _last_result is not None:
            result.setdefault('result',_last_result)
        if _journey is not None:
            result.pop('result',None)
            result['journey']={k:_journey[k] for k in ('id','key','stage')}
            result['journey']['destination_kind']=_journey.get('destination_kind','encore_station')
        return localize(json.loads(json.dumps(result)))


def enqueue(data):
    global _scan,_last_result,_processor_target,_processor_notice
    with _lock:
        if not _active or data.get('map_session')!=_gate.token:
            return False
        if data.get('action')=='select_processor':
            key=data.get('boss_id')
            if key not in processor_store.TARGETS or _busy or _state.get('status')!='ready':
                return False
            _processor_target=key
            _processor_notice=processor_store.TARGETS[key][0]+' selected. Close the map, stand at the processor and press F10.'
            return True
        if data.get('action')=='cancel':
            if _journey is None or data.get('journey_id')!=_journey['id']:
                return False
            _journey['cancel']=True
            return True
        if data.get('action')=='refresh':
            if _scan or _busy or _gate.pending is not None:
                return False
            _scan=True
            _state['status']='scanning'
            _state.pop('result',None)
            return True
        if data.get('action')!='teleport' or data.get('confirmed') is not True or _state.get('status')!='ready' or _busy:
            return False
        key=data.get('boss_id')
        if not isinstance(key,str) or (key not in _stations and key not in _waypoints) or time.monotonic()-_last_move<3:
            return False
        queued=_gate.put(data.get('map_session'),data.get('sequence'),key)
        if queued:
            _state.pop('result',None)
            _last_result=None
        return queued


def close():
    global _active,_scan,_world,_player,_state
    with _lock:
        _active=False;_scan=False;_gate.reset(None)
        _state={'status':'closed','bosses':[]}
    _stations.clear();_world=None;_player=None


def map_event(name):
    def callback(obj,args,_ret,_fn):
        global _active,_scan,_thread,_state
        try:
            if get_ident()!=_thread:
                return
            if str(args.OwningWidgetDef._name).casefold()!='def_menu_bigmap':
                return
            if name=='deactivate':
                close();return
            close()
            with _lock:
                _active=True;_scan=True;_gate.reset(uuid.uuid4().hex)
                _state={'status':'scanning','bosses':[],'map_session':_gate.token}
        except Exception as exc:
            close();log(**{'Teleport Failed Reason':str(exc)[:200]})
    return callback


def region_event(obj,args,_ret,_fn):
    global _region,_region_world
    if get_ident()!=_thread:
        return
    try:
        pc,pawn,world=contexts()
        if obj!=pc.PlayerState:
            return
        try:
            native=args.region
        except AttributeError:
            native=args.InRegionName
        name=def_name(native)
        _region=region_key(name);_region_world=WeakPointer(world)
        log(**{'Current Map':map_name(world),'Current Region':_region,'Native Region':name})
        # Region events update identity only. Scans wait for next map activation.
    except Exception:
        _region=None;_region_world=None


def drain(_obj,_args,_ret,_fn):
    global _scan,_lifecycle_ready,_thread,_record_requested
    if not _lifecycle_ready:
        if time.monotonic()<_defer_after:
            return
        _thread=get_ident()
        try:
            install_lifecycle()
            _lifecycle_ready=True
            log(**{'Lifecycle':'ready','GameThread':_thread})
        except Exception as exc:
            stop();log(**{'Teleport Failed Reason':'Lifecycle registration: '+str(exc)[:240]})
        return
    if get_ident()!=_thread:
        return
    with _lock:
        record=_record_requested;_record_requested=False
    if record:
        record_processor()
    if _journey is not None:
        poll_journey()
    if not _active:
        return
    # This lightweight pump checks Python flags only when idle; no per-frame scans.
    with _lock:
        scan=_scan;_scan=False;key=_gate.take();token=_gate.token;sequence=_gate.sequence
    if scan:
        discover()
    elif key:
        begin_travel(key,token,sequence)


def start():
    global _catalog,_locations,_routes,_health,_waypoints,_defer_after,_lifecycle_ready
    if _hooks:
        return
    _catalog=load()
    data=json.loads(files(__package__).joinpath('stations.json').read_text(encoding='utf8'))
    if data['schema']!=1:
        raise ValueError('Unsupported station metadata schema')
    _locations=data['stations']
    routes=json.loads(files(__package__).joinpath('travel_routes.json').read_text(encoding='utf8'))
    if routes['schema']!=1:
        raise ValueError('Unsupported travel route schema')
    _routes=routes['routes']
    points=json.loads(files(__package__).joinpath('waypoints.json').read_text(encoding='utf8'))
    if points.get('schema')!=1:
        raise ValueError('Unsupported extra waypoint schema')
    _waypoints=points['waypoints']
    for key,point in _waypoints.items():
        vector(point['position'])
        if point.get('id')!=key or point.get('kind')!='native_waypoint' or point['station'].split('.')[0].casefold()!=point['map_name']:
            raise ValueError('Invalid extra waypoint destination')
    install_processor_records(json.loads(files(__package__).joinpath('processor_defaults.json').read_text(encoding='utf8'))['positions'])
    try:
        install_processor_records(processor_store.read(destination()))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        log(**{'Processor Recording Load Failed':str(exc)[:240]})
    try:
        health=json.loads(files(__package__).joinpath('health_info.json').read_text(encoding='utf8'))
        _health=health['bosses'] if health.get('schema')==1 else {}
    except (OSError,ValueError,KeyError):
        _health={}
    _lifecycle_ready=False;_defer_after=time.monotonic()+5
    try:
        # Do not preempt legacy mods that mistake add_hook's return for hook
        # ownership. Add shared lifecycle observers after the startup import burst.
        path='/Script/GbxUIUMG.GbxUIUMGTickWidget:BP_TickWidget';phase=sdk.hooks.Type.PRE;ident=IDENT+'.Deferred'
        sdk.hooks.add_hook(path,phase,ident,drain)
        if not sdk.hooks.has_hook(path,phase,ident):
            raise RuntimeError('Cannot register deferred GameThread dispatcher')
        _hooks.append((path,phase,ident))
    except Exception:
        stop();raise


def install_lifecycle():
    cls=sdk.find_class('/Script/OakGame.OakUIScript_BigMap')
    specs=[(cls._find(n)._path_name(),sdk.hooks.Type.POST,n,map_event(n)) for n in ('Activate','deactivate')]
    specs.extend([
        ('/Script/OakGame.OakPlayerState:ServerEnteredWorldRegion',sdk.hooks.Type.POST,'Region',region_event),
        ('/Script/GbxGame.GbxPlayerState:ServerSetDiscoveryRegion',sdk.hooks.Type.POST,'DiscoveryRegion',region_event)])
    for path,phase,label,callback in specs:
        ident=IDENT+'.'+label
        sdk.hooks.add_hook(path,phase,ident,callback)
        if not sdk.hooks.has_hook(path,phase,ident):
            raise RuntimeError('Cannot register '+label)
        _hooks.append((path,phase,ident))


def stop():
    global _region,_region_world,_lifecycle_ready,_journey,_busy,_record_requested,_processor_target
    if _journey is not None and get_ident()==_thread:
        end_journey('Mod disabled')
    elif _journey is not None:
        # No UObject calls from another thread. The helper's native lifespan is
        # a bounded cleanup fallback; never resume this transaction on re-enable.
        _journey=None;_busy=False
    close();_region=None;_region_world=None
    _lifecycle_ready=False
    _record_requested=False;_processor_target=None
    while _hooks:
        sdk.hooks.remove_hook(*_hooks.pop())
