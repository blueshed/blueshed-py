'''
Created on Sep 28, 2013

@author: peterb
'''
from blueshed.handlers.base_handler import BaseHandler
from tornado.web import authenticated
from blueshed.utils.utils import dumps


class IndexHandler(BaseHandler):
    """
        A simple over-ride of BaseHandler to provide a
        service side rendered template that is
        authenticated. You can specify the page
        in the application handler declaration.
    """
        
    def initialize(self, page=None):
        self.page = page if page else "index.html"
    
    
    @authenticated
    def get(self):    
        user = dumps(self.control._get_user(self.current_user))
        mode = 'debug' if self.application.settings.get("debug") == 'yes' else 'built'
        self.render(self.page, user=user, mode=mode)
