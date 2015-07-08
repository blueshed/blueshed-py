'''
Created on Sep 28, 2013

@author: peterb
'''
import tornado.web
import logging


class PageHandler(tornado.web.RequestHandler):
    """
        Simple un-authenticated page handler, with a configurable
        page to be rendered.
    """
        
    def initialize(self, page=None):
        self.page = page if page else "index.html"
    
    
    def get(self,args=None):    
        logging.info(self.page)
        self.render(self.page)
