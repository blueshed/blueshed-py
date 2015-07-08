'''
Created on Apr 7, 2013

@author: peterb
'''
from blueshed.handlers.base_handler import BaseHandler

class InlineLoginHandler(BaseHandler):
    """
        Pass username and password as open arguments and login
        not secure, not good, but someone needed it.
    """
    
    def get(self, error=None):
        try:
            accl_key = self.control.login(self.get_argument("email"),
                                          self.get_argument("password"))
            self.set_current_user(accl_key)
            self.redirect(self.get_argument("next","/"))
        except:
            self.redirect(self.get_argument("next","/"))