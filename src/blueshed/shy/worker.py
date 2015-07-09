'''
Created on 16 Dec 2013

@author: peterb
'''
import logging

class PendingException(Exception):
    pass

class WorkDoneException(Exception):
    pass


class Worker(object):


    def __init__(self, shy, work, broadcast=None):
        self.shy = shy
        self.work = work
        self.broadcast = broadcast
        
        
    def open(self):
        for name in dir(self.work):
            if name[0] != "_":
                self.shy.subscribe(name)
                logging.info("subscribed to %s",name)

    
    def close(self):
        for name in dir(self.work):
            if name[0] != "_":
                self.shy.unsubscribe(name)
                logging.info("subscribed to %s",name)
                
                
    def handle(self, message, options):
        action = options.get(self.shy.QUEUE, self.broadcast) if options else self.broadcast
        if action:
            try:
                method = getattr(self.work, action)
                args = options.get(self.ARGS, {})
                result = method(**args)
                options["result"] = result
            except Exception as ex:
                options["error"] = str(ex)
            raise WorkDoneException()
            

    
    
        