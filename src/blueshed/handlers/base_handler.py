'''
Created on Apr 7, 2013

@author: peterb
'''
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    """
        This provides property access to the application settings
        for the control, cookie name, current user and
        provides a method to set the current user.
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
    
        
    def set_current_user(self, accl_key):
        self.set_secure_cookie(self.cookie_name, str(accl_key))

