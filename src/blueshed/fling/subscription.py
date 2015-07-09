'''
Created on Nov 2, 2013

@author: peterb
'''
from blueshed.fling.constants import TOPIC, QUEUE


class Subscription(object):
    
    def __init__(self, manager, listener, name):
        self.manage = manager
        self.listener = listener
        self.name = name
        
    
    def match(self, options):
        topic = options.get(TOPIC,options.get(QUEUE))
        return self.name == topic
        
    
    def listen(self, message, options):
        if options and not self.match(options):
            return
        self.listener.listen(message)
        return True
    
    
    def unsubscribe(self, name):
        return self.name == name