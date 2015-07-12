'''
Created on Sep 28, 2013

@author: peterb
'''
import logging
from tornado import websocket
from tornado.escape import json_decode
from blueshed.utils import utils
from tornado.log import access_log
import time


class WebsocketHandler(websocket.WebSocketHandler):
    """
        Simple authenticated websocket rpc of the control
    """
    
    @property
    def control(self):
        return self.application.settings['control']
    
    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')
    
    
    def get_current_user(self):
        accl = self.get_secure_cookie(self.cookie_name)
        if accl:
            return int(accl)

    @property
    def db_session(self):
        return self.application.settings['control'].session
    
    def open(self):
        logging.info("WebSocket opened")
        user = self.control.begin_web_session(self.current_user, self,
                                              self.request.remote_ip,
                                              self.request.headers)
        if user:
            self.broadcast({
                            "signal":"user",
                            "message": user,
                            "ws_version": self.application.settings.get('ws_version',1),
                            "model": self.control.describe(self.current_user)
                            })
        else:
            self.write_message(utils.dumps({'access_error':True}))
            self.close(reason="access control failure")
            

    def on_message(self, raw_message):
        
        start = time.time()
        
        message = json_decode(raw_message)
        action = message.get("action")
        
        try:
            logging.debug(message)
            args = message.get("args", {})
            
            method = getattr(self.control, action)
            
            if action=="make_impression":
                args["summary"] = self._request_summary()
                
            result = method(self.current_user, **args)
            self.write_message(utils.dumps({"result": result,
                                            "response_id": message.get("request_id")}))
            self.log_action(access_log.info, start, action, self.current_user)
            self.control._flush()
            
        except Exception as ex:
            logging.exception(ex)
            error = str(ex)
            self.write_message({"result": None,
                                "error" : error,
                                "response_id": message.get("request_id"),
                                })
            self.log_action(access_log.error, start, action, self.current_user, error)
            self.control._flush(ex)
            
    
    def log_action(self, logger, start, action, user, message=''):
        request_time = (time.time()-start)*1000
        logger("%s - %s - %s - %sms" % (action,self.current_user,message,request_time))
                             

    def on_close(self):
        logging.info("WebSocket closed")
        self.control.end_web_session(self)
        
    def force_close(self, code=None, reason=None):
        self.control._clients.remove(self)
        self.close(code, reason)
        
    def broadcast(self, message):
        self.write_message(utils.dumps(message))
        