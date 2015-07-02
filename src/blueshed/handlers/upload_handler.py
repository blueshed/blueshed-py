'''
Created on Jan 4, 2013

@author: peterb
'''
from tornado.web import StaticFileHandler
from tornado.escape import url_unescape
import logging
import os



class UploadHandler(StaticFileHandler):
    
    def _check_dir_(self, path):
        if not os.path.isdir(path):
            logging.info("creating upload directory %s", path)
            os.makedirs(path)
            
    
    def initialize(self, path, default_filename=None):
        self._check_dir_(path)
        StaticFileHandler.initialize(self, path, default_filename)
        

    def post(self,path=None):
        try:
            result = {}
            root = os.path.join(self.root,path) if path else self.root
            self._check_dir_(root)
            for key in self.request.files:
                for fileinfo in self.request.files[key]:
                    fname = url_unescape(fileinfo['filename'])
                    fNo = 0
                    fActual,fExt = os.path.splitext(fname)
                    files = os.listdir(root)
                    while fname in files:
                        fNo = fNo + 1
                        fname = "%s_%s%s" % (fActual,fNo,fExt)
                    
                    file_path = os.path.join(root,fname)
                    print(file_path, self.root)
                    logging.info("uploading %s", file_path)
                    with open(file_path,'wb') as fh:
                        fh.write(fileinfo['body'])
                    info = {}
                    result[key]={
                                 "name":fname,
                                 "info":info
                                 }
            self.write({"result":result})
        except Exception as ex:
            logging.exception(path)
            self.write({"error":str(ex)})
            
