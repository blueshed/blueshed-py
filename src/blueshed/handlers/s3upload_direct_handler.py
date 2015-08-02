'''
Created on 21 Jul 2015

@author: peterb
'''
from blueshed.utils import put_s3
'''
Created on 3 Mar 2015

@author: peterb
'''
import logging
from tornado.web import authenticated, asynchronous
import os
from blueshed.handlers.base_handler import BaseHandler
from blueshed.utils.pool import pool_call

class S3UploadDirectHandler(BaseHandler):
    
    def initialize(self, s3_config, bucket):
        BaseHandler.initialize(self)
        self.s3_config = s3_config
        self.bucket = bucket
        
      
    @authenticated
    def get(self, prefix=None):
        self.render("s3_upload.html")
        
                    
    @authenticated
    @asynchronous
    def post(self, prefix=None):
        try:            
            method = put_s3.main
            
            logging.info("prefix value %r",prefix)
            if prefix is None or prefix is '':
                prefix = self.get_argument("prefix", None)
                logging.info("prefix adjusted to %r",prefix)
                
            args = (self.current_user,
                    prefix,
                    self.request.files,
                    self.s3_config,
                    self.bucket)
            
            p = self.application.settings.get('pool')
            if p is not None:
                pool_call(p,method,self.on_result,*args)
            else:
                self.on_result(method(*args))
            
        except Exception as ex:
            logging.exception(ex)
            self.write({"error":str(ex)})
            self.finish()
 
 
    def on_result(self,result):
        result["tid"] = os.getpid()
        self.write(result)
        self.finish()
            
            