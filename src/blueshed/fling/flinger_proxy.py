'''
Created on Nov 2, 2013

@author: peterb
'''
import logging    
from blueshed.fling.fling_client import FlingClient
from blueshed.fling.subscription import Subscription
from tornado.ioloop import IOLoop
import time
import functools
from blueshed.fling.constants import COUNT, QUEUE


class FlingerProxy(object):

    def __init__(self, url="ws://localhost:7777/ws",reconnect=1):
        self.subscriptions = []
        self.requests = {}
        self.request_id_seed = 0;
        self.url = url
        self.client = FlingClient(url)
        self.client.on_open = self._on_open
        self.client.requested = self._requested
        self.client.listen = self._listen
        self.client.on_close = self._on_close
        self.connected = False
        self._reconnect = reconnect
        
        
    @property
    def _subscription_names_(self):
        return set([s.name for s in self.subscriptions])
    
    def _next_request_id_(self):
        self.request_id_seed += 1
        return self.request_id_seed
        
        
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
        self.client.subscribe(name)
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
            if name not in self._subscription_names_:
                self.client.unsubscribe(name)
        return result
        
        
    def broadcast(self, message, options=None):
        self.client.broadcast(message, options)

    
    def request_response(self, request, options=None):
        '''single request searching for response, may be pended'''
        request_id = self._next_request_id_()
        self.requests[request_id] = request
        logging.info(request)
        request_options = request.options if request.options else {}
        response = self.client.request_response(request.name, options, **request_options)
        response.add_done_callback(functools.partial(self._done, request_id, request))
            
    
    def _done(self, request_id, request, response):
        logging.info("_done %s",request_id)
        if self.requests.get(request_id):
            del self.requests[request_id]
            logging.info("proxy result %s %s", request_id, request.request_id)
            if response.exception():
                request.error = str(response.exception())
            else:
                request.result = response.result()
        
            
    def cancel_request(self, to_cancel):   
        ''' remove any waiting message '''
        for key,request in self.requests:
            if request == to_cancel:
                del self.requests[key]
                break;
        
        
    ''' over-ride these to perform tasks '''
    
    def _on_open(self):
        logging.info("open")
        self.connected = True

    
    def _requested(self, name, options=None, **kwargs):
        pass
    
    
    def _listen(self, message, options=None):
        if options and options.get(QUEUE) and options.get(COUNT) is None:
            options[COUNT]=1
        for subscription in [s for s in self.subscriptions]: #wallk a copy because items may be removed
            logging.debug('rebroadcasting %s',message)
            heard = subscription.listen(message, options)
            if heard is True and options is not None and options.get(QUEUE):
                options[COUNT] = options[COUNT]-1
                if options[COUNT]==0:
                    break
    
    
    def _on_close(self, error=None):
        self.connected = False
        logging.debug("closed %s %s", self.url, error)
        if self._reconnect is not None:
            IOLoop.instance().add_timeout(time.time()+self._reconnect, self.client._connect)
            logging.debug("reconnecting...")
            
            