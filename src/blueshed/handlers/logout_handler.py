'''
Created on Apr 4, 2013

@author: peterb
'''
from blueshed.handlers.base_handler import BaseHandler


class LogoutHandler(BaseHandler):
    """
        Simple logout handler that removes the cookie and
        forwards you to the site index - which will likely
        forward you to the login.
    """
    
    def get(self):
        self.clear_cookie(self.cookie_name)
        self.redirect("/")