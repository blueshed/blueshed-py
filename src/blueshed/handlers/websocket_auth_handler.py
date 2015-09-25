'''
Created on Sep 28, 2013

@author: peterb
'''
import logging
from tornado.escape import json_decode
from blueshed.utils import utils
from tornado.log import access_log
from blueshed.handlers.websocket_handler import WebsocketHandler
import time
from tornado.web import create_signed_value


class WebsockeAuthtHandler(WebsocketHandler):
    """
        Simple authenticated websocket rpc of the control
    """
    
    def gen_login_cookie(self,value):
        return create_signed_value(self.application.settings["cookie_secret"],
                                   self.cookie_name, value)


    def handle_login(self, message):
        accl_key = self.control.login(message.get("email"), 
                                      message.get("password"))
        self._current_user = accl_key
        self.send(utils.dumps({
                            "result":self.get_accl_user_dict(), 
                            "cookie":self.gen_login_cookie(accl_key).decode("utf-8"), 
                            "cookie_name":self.cookie_name, 
                            "response_id":message.get("request_id")
                            }))
        self._begin_web_session(self.current_user, 
                                self.request.ip, 
                                self.request.headers)
        

    def handle_register(self, message):
        accl_key = self.control.register(message.get("email"))
        self._current_user = accl_key
        self.send(utils.dumps({
                            "result":self.get_accl_user_dict(), 
                            "cookie":self.gen_login_cookie(accl_key), 
                            "cookie_name":self.cookie_name, 
                            "response_id":message.get("request_id")
                            }))
        self._begin_web_session(self.current_user, 
                                self.request.ip, 
                                self.request.headers)
        
    
    def _begin_web_session(self, current_user, ip, headers):
        user = self.control._begin_web_session(self.current_user, 
                                              self, ip, headers)
        self.broadcast({
                        "signal":"user",
                        "message": user,
                        "ws_version": self.application.settings.get('ws_version',1),
                        "ws_config": self.application.settings.get("ws_config",{}),
                        "model": self.control._fc_description,
                        "methods": self.control._fc_methods,
                        })

        
    
    def open(self):
        logging.info("WebSocket opened")
        if self.current_user:
            logging.info("reopening user: %s", self.current_user)
            self._begin_web_session(self.current_user, 
                                    self.request.remote_ip, 
                                    self.request.headers)
            

    def on_message(self, raw_message):
        
        start = time.time()
        
        message = json_decode(raw_message)
        action = message.get("action")
        
        try:
            logging.debug(message)
            args = message.get("args", {})
            
            if action == "register":
                self.handle_register(message)
            elif action == "login":
                self.handle_login(message)
            else:
                method = getattr(self.control, action)
                
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
        