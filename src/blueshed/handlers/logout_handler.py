'''
Created on Apr 4, 2013

@author: peterb
'''
from blueshed.handlers.base_handler import BaseHandler


class LogoutHandler(BaseHandler):
    
    def get(self):
        self.clear_cookie(self.cookie_name)
        self.redirect("/")