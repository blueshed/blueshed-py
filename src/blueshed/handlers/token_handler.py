'''
Created on Sep 28, 2013

@author: peterb
'''
from blueshed.handlers.base_handler import BaseHandler


class TokenHandler(BaseHandler):
        
    def initialize(self, page=None):
        self.page = page if page else "index.html"
    
    def get(self, token=None):
        if token:
            self.control.handle_token_read(token)
        self.redirect(self.page)
