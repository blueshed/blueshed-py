'''
Created on 21 Jul 2015

@author: peterb
'''
from tornado.web import authenticated
from blueshed.handlers.base_handler import BaseHandler


class ConfigHandler(BaseHandler):
    
    def initialize(self, config):
        self.config = config
        
        
    @authenticated
    def get(self, *args, **kwargs):
        self.write(self.config)