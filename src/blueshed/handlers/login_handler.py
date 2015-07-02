'''
Created on Apr 7, 2013

@author: peterb
'''
from blueshed.handlers.base_handler import BaseHandler
import logging

class LoginHandler(BaseHandler):
    
    def initialize(self, page=None):
        self.page = page if page else "login.html"
    
    
    def get(self, token=None, error=None, notice=None):
        if token:
            logging.info("token:%s",token)
            self.control.handle_token_visited(token[1:])
        email = self.get_argument("email",default=None)
        next_ = self.get_argument("next", "/")
        mode = "debug" if self.application.settings.get("debug",'no') != "no" else "built"
        self.render(self.page, 
                    email=email, 
                    error=error,
                    notice=notice,
                    mode=mode,
                    next=next_)
        
    
    def post(self, token=None):
        try:
            email = self.get_argument("email")
            if self.get_argument("submit", "") == "Forgotten password":
                self.control.forgotten_password(None, email)
                self.get(notice="Your password has been sent to your email address.")
            else:
                accl_key = self.control.login(self.get_argument("email"),
                                              self.get_argument("password"))
                self.set_current_user(accl_key)
                if token:
                    url = self.control.get_token_redirect_url(token[1:])
                    logging.info("token redirect {} {}".format(token,url))
                    self.redirect(url if url else self.get_argument("next","/"))
                else:
                    self.redirect(self.get_argument("next","/"))
        except Exception as ex:
            self.get(error=str(ex))