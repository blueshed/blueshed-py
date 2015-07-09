'''
Created on Nov 2, 2013

@author: peterb
'''
import logging  # @UnresolvedImport
from tornado.websocket import WebSocketHandler
from blueshed.fling.request import Request
from blueshed.fling import utils

class FlingHandler(WebSocketHandler):
    
    
    def initialize(self, worker=True):
        WebSocketHandler.initialize(self)
        self.worker = worker
        self.callbacks = {}
        self.requests = []
        self.closing = False
    
    @property
    def flinger(self):
        return self.application.settings["flinger"]


    def open(self):
        self.set_nodelay(True) 
        logging.info("client opened")


    def handled(self, request):
        if self.closing is True: return
        response = {
            "result": request.result,
            "error": request.error,
            "response_id": request.request_id
        }
        self.requests.remove(request)
        logging.debug(response)
        self.write_message(utils.dumps(response))
        logging.info("wrote %s",request.request_id)
        
    
    
    def on_message(self, raw_message):
        logging.info(raw_message)
        message = utils.loads(raw_message)
        request_id = message.get("request_id")
        method = message["method"]
        args = message.get("args")
        try:
            if method == "subscribe":
                self.flinger.subscribe(self,args.get("name"))
            elif method == "unsubscribe":
                self.flinger.unsubscribe(self,args.get("name"))
            elif method == "broadcast":
                self.flinger.broadcast(args["message"],args.get("options"))
            elif method == "handle":
                request = Request(args["name"],args.get("request_options"), self.handled, request_id)
                self.requests.append(request)
                self.flinger.request_response(request, args.get("options"))
            elif method == "handled":
                callback = self.callbacks.get(request_id)
                if callback:
                    del self.callbacks[request_id]
                    if message.get("result"):
                        callback.result = message["result"]
                    else:
                        callback.error = message["error"]
                if self.worker is True:
                    self.flinger.subscribe(self,callback.name)
        except:
            logging.exception(raw_message)
        

    def on_close(self):
        self.closing = True
        ''' remove all subscriptions for this listener '''
        self.flinger.remove_listener(self)
        ''' cancel all request callback '''
        for request in self.requests:
            self.flinger.cancel_request(request)
            request.cancel()
            logging.info("cancelled %s[%s]",request.name, request.request_id)
        for request_id,request in self.callbacks.items():
            request.cancel()
        self.requests = None
        logging.info("client closed")
        
    
    def listen(self, message, options=None):
        if self.closing is True: return
        if isinstance(message, Request):
            if self.worker is True:
                self.flinger.unsubscribe(self,message.name)
            self.callbacks[message.request_id]=message
            logging.debug('handling %s',message.request_id)
            self.write_message(utils.dumps({"request_id":message.request_id,
                                            "name": message.name,
                                            "options":message.options}))
        else:
            logging.debug('listening %s',message)
            self.write_message(utils.dumps({"message":message, 
                                            "options":options}))
        return True
        
