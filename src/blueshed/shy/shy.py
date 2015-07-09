'''
Created on Nov 2, 2013

@author: peterb
'''
import logging


class Shy(object):
    
    QUEUE = "queue"

    def __init__(self):
        self.subscriptions = []        
        
        
    def subscribe(self, listener, name=None):
        self.subscriptions.append((name,listener))
        logging.info("subscription to %s",name)
    
    
    def unsubscribe(self, listener, name=None):
        self.subscriptions = filter(lambda s: s!=(name,listener), self.subscriptions)
        logging.info("unsubscribed to %s",name)
        
        
    def broadcast(self, message, options=None):
        queue = options.get(self.QUEUE) if options else None
        for name,listener in self.subscriptions:
            if name  is None or name == queue:
                listener(message, options)
                            
            
            