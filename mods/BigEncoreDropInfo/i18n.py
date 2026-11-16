# -*- coding: utf-8 -*-
"""Chinese display labels only; canonical names, IDs and travel data stay unchanged."""
from functools import lru_cache
from importlib.resources import files
import json


@lru_cache(maxsize=1)
def _data():
    return json.loads(files(__package__).joinpath("i18n.json").read_text(encoding="utf-8"))


def translate(value):
    if not isinstance(value, str):
        return value
    data = _data()
    if value in data["phrases"]:
        return data["phrases"][value]
    if value in data["labels"]:
        return data["labels"][value]
    result = value
    for source, target in sorted(data["fragments"].items(), key=lambda pair: -len(pair[0])):
        result = result.replace(source, target)
    for source, target in sorted(data["labels"].items(), key=lambda pair: -len(pair[0])):
        if source in result:
            result = result.replace(source, target)
    return result


def localize(value):
    if isinstance(value, list):
        return [localize(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: localize(item) for key, item in value.items()}
    for key in ("name", "kind_label", "region_name", "note", "destination_note", "reason", "processor_notice"):
        if isinstance(value.get(key), str) and value[key]:
            result.setdefault("cn_" + key, translate(value[key]))
    if "Teleport Failed Reason" in value:
        result["cn_failure_reason"] = translate(value["Teleport Failed Reason"])
    for key in ("boss_names", "labels"):
        if isinstance(value.get(key), list):
            result.setdefault("cn_" + key, [translate(item) for item in value[key]])
    if "element" in value:
        result.setdefault("cn_element", translate(value["element"]))
    if "health_label" in value:
        result.setdefault("cn_health_label", translate(value["health_label"]))
    # Catalog rows retain all original matching aliases in their original order.
    if isinstance(value.get("map_names"), list):
        aliases = [translate(item) for item in value["map_names"] if isinstance(item, str)]
        aliases += [result.get("cn_name", "")]
        result.setdefault("cn_map_names", list(dict.fromkeys(item for item in aliases if item)))
    for key in result.keys() & _data()["boss_aliases"].keys():
        aliases = _data()["boss_aliases"][key]
        if isinstance(result[key], dict) and "map_names" in result[key]:
            result[key]["cn_map_names"] = list(dict.fromkeys(result[key].get("cn_map_names", []) + aliases))
    return result
