'''
Date, json and AWS utils

Created on Nov 1, 2013

@author: peterb
'''
import json
from decimal import Decimal    
import datetime
import collections
import time
import random
import string
        
class AWSConfig(object):
    
    def __init__(self, key, secret):
        self.aws_access_key_id = key
        self.aws_secret_access_key = secret
        
    def __repr__(self, *args, **kwargs):
        return "AWSConfig(key={},secret={})".format(self.aws_access_key_id,
                                                    self.aws_secret_access_key)


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
        
        
def loads(*args, **kwargs):
    return json.loads(*args, **kwargs)


def dumps(o, **kwargs):
    return json.dumps(o, cls=DateTimeEncoder, **kwargs)



def parse_date(value):
    """Returns a Python datetime.datetime object, the input must be in some date ISO format""" 
    result = None
    if value:
        try:
            result = datetime.datetime.strptime(value,"%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            try:
                result =  datetime.datetime.strptime(value,"%Y-%m-%d %H:%M:%S.%f")
            except:
                try:
                    result =  datetime.datetime.strptime(value,"%Y-%m-%d %H:%M:%S")
                except:
                    result =  datetime.datetime.strptime(value,"%Y-%m-%d")
                
    return result

def parse_time(value):
    result = None
    if value:
        try:
            result = datetime.datetime.strptime(value,"%H:%M:%S.%f")
        except:
            try:
                result =  datetime.datetime.strptime(value,"%H:%M:%S")
            except:
                result =  datetime.datetime.strptime(value,"%H:%M")
    return result

def parse_unix_time(value):
    return datetime.datetime.fromtimestamp(int(value))

def to_unix_time(value):
    return time.mktime(value.timetuple()) * 1000


def patch_tornado():
    # to provide svg and gzip svg support
    import mimetypes
    import tornado.web
    
    mimetypes.add_type('image/svg+xml', '.svg') #because its not there!
    tornado.web.GZipContentEncoding.CONTENT_TYPES.add('image/svg+xml')
    mimetypes.add_type('application/font-woff', '.woff') #because its not there!
    mimetypes.add_type('application/font-woff2', '.woff2') #because its not there!



def gen_token(length=32):
    return ''.join(random.choice(string.hexdigits) for i in range(length))


