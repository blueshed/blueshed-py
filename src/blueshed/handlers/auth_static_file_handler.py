'''
Created on 25 Jun 2015

@author: peterb
'''
from tornado.web import authenticated, StaticFileHandler


class AuthStaticFileHandler(StaticFileHandler):
    
    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')
    
    
    def get_current_user(self):
        accl = self.get_secure_cookie(self.cookie_name)
        if accl:
            return int(accl)
        
    
    @authenticated
    def get(self, path, include_body=True):
        return StaticFileHandler.get(self, path, include_body)
        