# -*- coding: utf-8 -*-
"""Map keyword aliases to the exact reflected Unreal function parameter names."""


def named(function,properties):
    names={str(p.Name).casefold():str(p.Name) for p in properties}
    def call(*args,**kwargs):
        mapped={}
        for key,value in kwargs.items():
            original=names.get(key.casefold())
            if original is None:
                raise TypeError('Unknown native parameter: '+key)
            if original in mapped:
                raise TypeError('Duplicate native parameter: '+original)
            mapped[original]=value
        return function(*args,**mapped)
    return call
