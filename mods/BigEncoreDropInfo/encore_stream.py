# -*- coding: utf-8 -*-
"""Short-lived native streaming source at an exact Encore destination.

Does not relocate the player's streaming source or change data-layer unlocks.
All entry points are called by the runtime's GameThread dispatcher only.
"""
import math
import unrealsdk as sdk
from unrealsdk.unreal import WeakPointer
from .native_call import named


def bind(obj,name,required,optional=None):
    function=obj.Class._find(name)
    if type(function).__name__!='UFunction':
        raise RuntimeError(name+': native function unavailable')
    props={str(p.Name).casefold():p for p in function._properties() if int(p.PropertyFlags)&0x80}
    optional=optional or {}
    if not set(required)<=props.keys() or props.keys()-required.keys()-optional.keys():
        raise RuntimeError(name+': unsupported native parameters')
    for key,p in props.items():
        allowed=(required|optional)[key]
        if type(p).__name__.removeprefix('Z') not in allowed.split('|'):
            raise RuntimeError(name+': unsupported parameter '+key)
        if key in ('spawntransform','relativetransform') and p.Struct._path_name()!='/Script/CoreUObject.Transform':
            raise RuntimeError(name+': unexpected transform type')
    return named(getattr(obj,name),props.values()),set(props)


def returned(value):
    return value[0] if isinstance(value,tuple) else value


class Lease:
    def __init__(self,world,helper,component,checked,bool_call):
        self.world=WeakPointer(world);self.helper=WeakPointer(helper);self.component=WeakPointer(component)
        self.checked=checked;self.bool_call=bool_call

    def ready(self,world):
        if self.world()!=world:
            raise RuntimeError('Destination world changed during streaming')
        component=self.checked(self.component())
        return self.bool_call(component,'IsStreamingCompleted')

    def close(self):
        helper=self.helper()
        if helper is None:
            return
        try:
            helper=self.checked(helper)
            destroy,_=bind(helper,'K2_DestroyActor',{})
            destroy()
        finally:
            self.helper=lambda:None;self.component=lambda:None


def create(pc,pawn,world,position,checked,bool_call,world_of):
    """Preflight reflected APIs before spawning a non-colliding TargetPoint."""
    system=sdk.find_object('Object','/Script/Engine.Default__GameplayStatics')
    if system is None or WeakPointer(system)() is None or system.Class._path_name()!='/Script/Engine.GameplayStatics':
        raise RuntimeError('Gameplay statics unavailable')
    # CDOs are used only to validate signatures, never as world/actor instances.
    actor_default=sdk.find_object('Object','/Script/Engine.Default__TargetPoint')
    source_default=sdk.find_object('Object','/Script/Engine.Default__WorldPartitionStreamingSourceComponent')
    if actor_default is None or source_default is None:
        raise RuntimeError('Native destination streaming classes unavailable')
    begin,begin_fields=bind(system,'BeginDeferredActorSpawnFromClass',{
        'worldcontextobject':'ObjectProperty','actorclass':'ClassProperty','spawntransform':'StructProperty',
        'collisionhandlingoverride':'EnumProperty|ByteProperty','owner':'ObjectProperty','returnvalue':'ObjectProperty'},
        {'transformscalemethod':'EnumProperty|ByteProperty'})
    finish,finish_fields=bind(system,'FinishSpawningActor',{
        'actor':'ObjectProperty','spawntransform':'StructProperty','returnvalue':'ObjectProperty'},
        {'transformscalemethod':'EnumProperty|ByteProperty','bisdefaulttransform':'BoolProperty'})
    component_args={'class':'ClassProperty','bmanualattachment':'BoolProperty','relativetransform':'StructProperty',
        'bdeferredfinish':'BoolProperty','returnvalue':'ObjectProperty'}
    bind(actor_default,'AddComponentByClass',component_args)
    bind(actor_default,'SetLifeSpan',{'inlifespan':'FloatProperty'})
    bind(actor_default,'K2_DestroyActor',{})
    bind(actor_default,'K2_GetActorLocation',{'returnvalue':'StructProperty'})
    bind(source_default,'EnableStreamingSource',{})
    bind(source_default,'IsStreamingCompleted',{'returnvalue':'BoolProperty'})
    collision=sdk.find_enum('/Script/Engine.ESpawnActorCollisionHandlingMethod').AlwaysSpawn
    target_state=sdk.find_enum('/Script/Engine.EStreamingSourceTargetState').Activated
    source_class=sdk.find_class('/Script/Engine.WorldPartitionStreamingSourceComponent')
    transform=sdk.make_struct('/Script/CoreUObject.Transform',
        Translation=sdk.make_struct('/Script/CoreUObject.Vector',X=position[0],Y=position[1],Z=position[2]),
        Rotation=sdk.make_struct('/Script/CoreUObject.Quat',X=0.,Y=0.,Z=0.,W=1.),
        Scale3D=sdk.make_struct('/Script/CoreUObject.Vector',X=1.,Y=1.,Z=1.))
    identity=sdk.make_struct('/Script/CoreUObject.Transform',
        Rotation=sdk.make_struct('/Script/CoreUObject.Quat',X=0.,Y=0.,Z=0.,W=1.),
        Scale3D=sdk.make_struct('/Script/CoreUObject.Vector',X=1.,Y=1.,Z=1.))
    begin_extra={};finish_extra={}
    if 'transformscalemethod' in begin_fields or 'transformscalemethod' in finish_fields:
        scale=sdk.find_enum('/Script/Engine.ESpawnActorScaleMethod').MultiplyWithRoot
        if 'transformscalemethod' in begin_fields:begin_extra['TransformScaleMethod']=scale
        if 'transformscalemethod' in finish_fields:finish_extra['TransformScaleMethod']=scale
    if 'bisdefaulttransform' in finish_fields:finish_extra['bIsDefaultTransform']=False
    helper=None
    try:
        helper=checked(returned(begin(WorldContextObject=pawn,ActorClass=sdk.find_class('/Script/Engine.TargetPoint'),
            SpawnTransform=transform,CollisionHandlingOverride=collision,Owner=pc,**begin_extra)))
        life,_=bind(helper,'SetLifeSpan',{'inlifespan':'FloatProperty'});life(InLifespan=120.)
        helper=checked(returned(finish(Actor=helper,SpawnTransform=transform,**finish_extra)))
        if world_of(helper)!=world:
            raise RuntimeError('Streaming helper spawned in a different world')
        location_fn,_=bind(helper,'K2_GetActorLocation',{'returnvalue':'StructProperty'})
        location=location_fn()
        if math.dist((location.X,location.Y,location.Z),position)>2:
            raise RuntimeError('Streaming helper transform mismatch')
        add,_=bind(helper,'AddComponentByClass',component_args)
        component=checked(returned(add(Class=source_class,bManualAttachment=True,
            RelativeTransform=identity,bDeferredFinish=False)))
        # Activated loads collision and actors; Loaded alone is insufficient.
        component.TargetState=target_state
        enable,_=bind(component,'EnableStreamingSource',{});enable()
        return Lease(world,helper,component,checked,bool_call)
    except Exception:
        if helper is not None:
            try:
                destroy,_=bind(helper,'K2_DestroyActor',{});destroy()
            except Exception:
                pass # SetLifeSpan is a second bounded cleanup path.
        raise
