'''
Created on Nov 22, 2012

@author: peterb
'''

from sockjs.tornado import SockJSConnection  # @UnresolvedImport
import logging
import time
from tornado.log import access_log
from tornado.escape import json_decode
from blueshed.utils import utils

class SockJSHandler(SockJSConnection):
    ''' 
        Using the SockJS WebSocket Connection - monkey patched to work like websocket_handler
    '''
    
    def __init__(self, *args, **kwargs):
        SockJSConnection.__init__(self, *args, **kwargs)
        self.application = None
        self.request = None
        self._access_context_ = None
        
        
    def get_current_user(self):
        return self.get_secure_cookie(self.application.settings.get('cookie_name'))
    
    def get_secure_cookie(self, name, value=None, max_age_days=31):
        return self.session.handler.get_secure_cookie(name, value=value, max_age_days=max_age_days)
    
    @property
    def control(self):
        return self.application.settings.get('control')


    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = self.get_current_user()
        return int(self._current_user)

    
    def on_open(self, request):  
        self.request = request
        self.application = self.session.handler.application
        logging.info("SockJS opened")
        user = self.control.begin_web_session(self.current_user, 
                                              self, request.ip, request.headers)
        if user:
            self.broadcast({
                            "signal":"user",
                            "message": user
                            })
        else:
            self.send(utils.dumps({'access_error':True}))
            self.close(reason="access control failure")
        
        
    def on_close(self):
        logging.info("SockJS closed")
        self.control.end_web_session(self)


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
            self.send(utils.dumps({"result": result,
                                            "response_id": message.get("request_id")}))
            self.log_action(access_log.info, start, action, self.current_user)
            self.control._flush()
            
        except Exception as ex:
            logging.exception(ex)
            error = str(ex)
            self.send(utils.dumps({"result": None,
                                "error" : error,
                                "response_id": message.get("request_id"),
                                }))
            self.log_action(access_log.error, start, action, self.current_user, error)
            self.control._flush(ex)
        
        
    def log_action(self, logger, start, action, user, message=''):
        request_time = (time.time()-start)*1000
        logger("%s - %s - %s - %sms" % (action,self.current_user,message,request_time))
    
    
    def broadcast(self, message):
        self.send(utils.dumps(message))
        
