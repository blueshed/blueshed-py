'''
Created on 8 Jul 2015

@author: peterb
'''
from blueshed.handlers.rest_handler import RestHandler as BaseHandler
from tornado.web import HTTPError


class RestHandler(BaseHandler):
    
    def initialize(self, auth_header='blueshed-auth-token'):
        self.auth_header = auth_header 
        BaseHandler.initialize(self)
    
    def authenticate(self):
        token = self.request.headers.get(self.auth_header)
        if token is None:
            raise HTTPError(403)
        user = self.control.get_token_user(token)
        if user is None:
            raise HTTPError(403)
    
    def get(self, resource_path):
        self.authenticate()
        BaseHandler.get(self, resource_path)
        
    def put(self, resource_path):
        self.authenticate()
        BaseHandler.put(self, resource_path)
        
    def post(self, resource_path):
        self.authenticate()
        BaseHandler.post(self, resource_path)
        
    def delete(self, resource_path):
        self.authenticate()
        BaseHandler.delete(self, resource_path)