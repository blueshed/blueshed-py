'''
Created on Nov 12, 2013

@author: peterb
'''
import jsonpickle
import logging
from blueshed.fling.fling_rpc import FlingRPC
from blueshed.fling.constants import LOG_FORMAT

class FlingPickle(object):
        
    def pickled_work(self, obj, method, args=None, kwargs=None):
        object = jsonpickle.decode(obj)
        if args is None: args = []
        if kwargs is None: kwargs = {}
        getattr(object,method)(*args,**kwargs)
        return jsonpickle.encode(object)

        
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format=LOG_FORMAT)
    FlingRPC.serve(FlingPickle(), "ws://localhost:7777/ws")
    