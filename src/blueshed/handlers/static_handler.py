'''
Created on Jul 29, 2011

@author: peterb
'''
from tornado.web import StaticFileHandler, HTTPError
import os

"""
Sample config of application
    static_path=resource_filename("daisy","www/static"),
    static_handler_class=StaticHandler,
    static_handler_args={"other":resource_filename("blueshed","www/static")},
"""


class StaticHandler(StaticFileHandler):
    """
        Allows you to chain static folders.
        If not found in the first will look in the next before
        returning a 404
    """
    
    def initialize(self, path, default_filename=None, others=None):
        StaticFileHandler.initialize(self, path, default_filename)
        self._others = others if others else self.application.settings["static_handler_args"]["others"]
        
    
    def validate_absolute_path(self, root, absolute_path):
        
        if (os.path.isdir(absolute_path) and
                self.default_filename is not None):
            # need to look at the request.path here for when path is empty
            # but there is some prefix to the path that was already
            # trimmed by the routing
            if not self.request.path.endswith("/"):
                self.redirect(self.request.path + "/", permanent=True)
                return
            absolute_path = os.path.join(absolute_path, self.default_filename)

        if os.path.isfile(absolute_path):
            return absolute_path
        
        root = os.path.abspath(root)
        path = absolute_path[len(root):]
        for other in self._others:
            absolute_path = os.path.abspath(os.path.join(other, path[1:]))
            if os.path.isfile(absolute_path):
                return absolute_path
            
        if not os.path.exists(absolute_path):
            raise HTTPError(404)
        if not os.path.isfile(absolute_path):
            raise HTTPError(403, "%s is not a file", self.path)
        return absolute_path
