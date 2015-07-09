'''
Created on Nov 12, 2013

@author: peterb
'''
import logging
import time
from blueshed.fling.fling_client import FlingClient
from tornado.ioloop import IOLoop

class FlingRPC(FlingClient):
    
    def __init__(self, target, url="ws://localhost:7777/ws", reconnect=1):
        FlingClient.__init__(self, url=url)
        self._target = target
        self._reconnect = reconnect
        
    def on_open(self):
        for name in dir(self._target):
            if name[0] != "_":
                self.subscribe(name)
                logging.info("subscribed to %s",name)

    
    def requested(self, name, options=None, **kwargs):
        logging.debug("requested %s[%s] %s",name,options,kwargs)
        return getattr(self._target,name)(**kwargs)
    
    
    def on_close(self, error=None):
        logging.debug("closed %s %s", self.url, error)
        if self._reconnect is not None:
            IOLoop.instance().add_timeout(time.time()+self._reconnect, self._connect)
            logging.debug("reconnecting...")


    @classmethod    
    def serve(cls, target, url="ws://localhost:7777/ws"):
        service = cls(target,url)
        IOLoop.instance().start()
        return service
    
    

        
        