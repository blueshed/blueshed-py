'''
Created on Nov 2, 2013

@author: peterb
'''
import logging
from blueshed.fling.constants import QUEUE, COUNT
from blueshed.fling.subscription import Subscription
    

class Flinger(object):

    def __init__(self):
        self.subscriptions = []
        self.requests = []
        
        
    def remove_listener(self, listener):
        ''' no i can't '''
        subscriptions = list(filter(lambda s: s.listener==listener,
                                    self.subscriptions))
        for subscription in subscriptions:
            self.unsubscribe(subscription.listener, subscription.name)
            logging.debug("removed listener to %s",subscription.name)
        
        
    def subscribe(self, listener, name=None):
        '''it's me, i can'''
        self.subscriptions.append(Subscription(self, listener,name))
        logging.info("subscription to %s",name)
        self.flush_queue(name)
        return True
    
    
    def unsubscribe(self, listener, name=None):
        '''not intereted any more'''
        result = False
        if self.subscriptions:
            subscriptions = list(filter(lambda s: s.listener==listener and s.unsubscribe(name),
                                        self.subscriptions))
            for subscription in subscriptions:
                self.subscriptions.remove(subscription)
                logging.info("unsubscribed to %s",name)
                result = True
        return result
        
        
    def broadcast(self, message, options=None):
        ''' find someone to listen '''
        if options and options.get(QUEUE) and options.get(COUNT) is None:
            options[COUNT]=1
        for subscription in [s for s in self.subscriptions]: #wallk a copy because items may be removed
            logging.debug('broadcasting %s',message)
            heard = subscription.listen(message, options)
            if heard is True and options is not None and options.get(QUEUE):
                options[COUNT] = options[COUNT]-1
                if options[COUNT]==0:
                    break

    
    def request_response(self, request, options=None):
        '''single request searching for response, may be pended'''
        logging.debug('handling %s',request)
        try:
            options = options if options else {}
            options[QUEUE]=request.name
            self.broadcast(request, options)
            if options[COUNT] > 0:
                logging.info("request queued %s",request.request_id)
                self.requests.append((request,options))
        except Exception as ex:
            request.set_error(str(ex))
            logging.debug('failed to handle %s',ex)
            
            
    def cancel_request(self, to_cancel):  
        ''' remove any waiting message '''
        for item in self.requests:
            if item[0] == to_cancel:
                self.requests.remove(item)
                break;
        
            
    def flush_queue(self, name):
        ''' check to see if there is a waiting message for this queue '''
        for item in self.requests:
            request,options = item
            if request.name == name:
                logging.info("broadcast from requests %s",request.request_id)
                self.broadcast(request, options)
                if options[COUNT] == 0:
                    self.requests.remove(item)
                    break
        
            
            