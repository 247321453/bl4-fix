# -*- coding: utf-8 -*-
"""Pure, independently testable policy. No engine imports or guessed coordinates."""
import math
import re

REGIONS = {'grasslands': 'Fadefields', 'shatteredlands': 'Carcadia Burn',
           'mountains': 'Terminus Range', 'city': 'Dominion', 'elpis': 'Elpis'}


def region_key(name):
    # Native region identifiers, never a viewed-map title or nearest landmark.
    tokens = re.split(r'[^a-z0-9]+', str(name).casefold())
    aliases = {'gra': 'grasslands', 'sha': 'shatteredlands', 'mtn': 'mountains',
               'mountain': 'mountains', 'shatterlands': 'shatteredlands',
               'dominion': 'city', 'elp': 'elpis'}
    for t in tokens:
        t = aliases.get(t, t)
        if t in REGIONS:
            return t
    return None


def station_region(station):
    match = re.fullmatch(r'uilocation_bossfight_(?:(?:fortress|vault)_)?(gra|sha|mtn|city|elp)\d+', station)
    return region_key(match[1]) if match else None


def vector(v):
    v = tuple(float(x) for x in v)
    if len(v) != 3 or not all(math.isfinite(x) and abs(x) < 1e8 for x in v):
        raise ValueError('Invalid world vector')
    return v


def candidates(location, yaw):
    """Try forward first, then front diagonals; never machine center/back."""
    x, y, z = vector(location)
    yaw = float(yaw)
    if not math.isfinite(yaw):
        raise ValueError('Invalid station rotation')
    a = math.radians(yaw)
    for forward, right in ((240, 0), (300, 150), (300, -150), (400, 0)):
        yield (x + math.cos(a)*forward - math.sin(a)*right,
               y + math.sin(a)*forward + math.cos(a)*right, z)


def landing(hit, candidate, radius, half_height):
    """Reject steep floors, water/void via caller collision checks, large drops."""
    point = vector(hit['point'])
    normal = vector(hit['normal'])
    if not hit['blocking'] or hit['penetrating'] or normal[2] < .75:
        raise ValueError('No walkable ground')
    if not (10 <= radius <= 150 and radius <= half_height <= 250):
        raise ValueError('Unexpected player capsule')
    if abs(point[2]-candidate[2]) > 240:
        raise ValueError('Ground too far from station')
    return point[0], point[1], point[2] + half_height + 4


class Requests:
    """Bounded token/sequence gate; caller owns lock, engine work stays elsewhere."""
    def __init__(self):
        self.reset(None)

    def reset(self, token):
        self.token, self.sequence, self.pending = token, -1, None

    def put(self, token, sequence, boss):
        if not self.token or token != self.token or type(sequence) is not int:
            return False
        if sequence <= self.sequence or self.pending is not None or not isinstance(boss, str) or len(boss)>100:
            return False
        self.sequence = sequence
        self.pending = boss
        return True

    def take(self):
        result, self.pending = self.pending, None
        return result
