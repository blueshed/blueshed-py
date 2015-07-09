'''
Created on Nov 2, 2013

@author: peterb
'''
from tornado.websocket import websocket_connect
import logging  # @UnresolvedImport
from tornado.concurrent import Future  # @UnresolvedImport
from blueshed.fling import utils


class FlingClient(object):


    def __init__(self, url="ws://localhost:7777/ws"):
        self.url = url
        self.status = "closed"
        self._next_request_id = 0
        self._requests = {}
        self._connect()
        
        
    def _connect(self):
        self._connection = websocket_connect(self.url,
                                             callback=self._connected,
                                             connect_timeout=1)
    
    
    def _connected(self, connection):
        if connection.exception():
            self.on_close(connection.exception())
        else:
            self._connection = connection.result()
            self.status = "open"
            logging.debug("connected to: %s",self.url)
            self.on_open()
            self._connection.read_message(self._on_read)
    
    
    def _on_read(self, reading):
        if reading.exception():
            logging.exception(reading.exception())
            self.on_close(reading.exception())
        else:
            try:
                self._on_message(reading.result())
                self._connection.read_message(self._on_read)
            except Exception as ex:
                logging.warn(ex)
                self.on_close(ex)
        

    def _on_message(self, raw_message):
        logging.info(raw_message)
        message = utils.loads(raw_message)
        if message.get("response_id"):
            request = self._requests.get(message.get("response_id"))
            if request:
                if message.get("result"):
                    request.set_result(message["result"])
                else:
                    request.set_exception(message["error"])
        elif message.get("request_id"):
            response = {"request_id": message["request_id"],
                        "method": "handled"}
            try:
                response['result']=self.requested(message["name"], 
                                                  **message.get("options"))
            except Exception as ex:
                response["error"] = str(ex)
            logging.info(response)
            self.write_message(response)
        else:
            self.listen(message.get("message"),
                        message.get("options"))
            
            
    def write_message(self, message):
        self._connection.write_message(utils.dumps(message))
        
    
    ''' fling methods '''
        
    def subscribe(self, name=None):
        self.write_message({"method":"subscribe", "args":{"name":name}})
        
        
    def unsubscribe(self, name=None):
        self.write_message({"method":"unsubscribe", "args":{"name":name}})
        
        
    def broadcast(self, message, options=None):
        self.write_message({"method":"broadcast", 
                                        "args":{"message": message,
                                                "options": options}})
        
        
    def request_response(self, name, options=None, **kwargs):
        self._next_request_id = self._next_request_id + 1
        response = Future()
        self._requests[self._next_request_id]=response
        self.write_message({"method":"handle", 
                            "request_id": self._next_request_id,
                            "args":{"name": name,
                                    "request_options": kwargs,
                                    "options": options}})
        return response
        
        
    ''' over-ride these to perform tasks '''
    
    def on_open(self):
        pass

    
    def requested(self, name, options=None, **kwargs):
        pass
    
    
    def listen(self, message, options=None):
        pass
    
    
    def on_close(self, error=None):
        pass
    

