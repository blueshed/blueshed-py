'''
Created on Apr 15, 2013

@author: peterb
'''
import json
from decimal import Decimal
import collections

class Dict(dict):
    """
        A dict that allows for object-like property access syntax.
    """
    
    def __getattr__(self, name):
        if name[0] == '_': return dict.__getattr__(self.name)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


def loads(*args, **kwargs):
    #use Dict instead of dict
    if not 'object_hook' in kwargs:
        kwargs['object_hook']=Dict
    return json.loads(*args, **kwargs)


def dumps(o, **kwargs):
    return json.dumps(o, cls=DateTimeEncoder, **kwargs)


class DateTimeEncoder(json.JSONEncoder):
    """Encodes datetimes and Decimals"""
    
    def default(self, obj):  
        try:      
            if hasattr(obj, 'isoformat'):
                return obj.isoformat().replace("T"," ")
            elif isinstance(obj, Decimal):
                return float(obj)
            elif hasattr(obj,"to_json") and isinstance(getattr(obj,"to_json"), collections.Callable):
                return obj.to_json()
            return json.JSONEncoder.default(self, obj)
        except:
            raise
#            return str(obj)
        


def toJSON(obj):
    return dumps(obj).replace("</", "<\\/")