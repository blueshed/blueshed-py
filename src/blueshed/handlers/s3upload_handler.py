'''
Created on 3 Mar 2015

@author: peterb
'''
import tornado.web
from PIL import Image
import logging
import io
import os
from blueshed.utils.bucket import Bucket

class S3UploadHandler(tornado.web.RequestHandler):
    """
        Simple upload hanlder to save images to s3.
    """
    
    TYPE_MAP = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".gif": "GIF"
    }
    
    def initialize(self, bucket, thumb_size=None):
        tornado.web.RequestHandler.initialize(self)
        self.bucket_name = bucket
        self.thumb_size = thumb_size
    
    @property
    def aws_config(self):
        return self.application.settings.get('aws_config')

    def post(self,path):
        try:
            bucket = Bucket.get_bucket_by_name(self.aws_config,self.bucket_name)
            result = {}
            for key in self.request.files:
                for fileinfo in self.request.files[key]:
                    fname = fileinfo['filename']
                    fActual,fExt = os.path.splitext(fname)
                    fType = self.TYPE_MAP[fExt.lower()]
                    logging.info("uploading %s - %s", fname, path)
                    s3KeyName = "{}/{}".format(path,fname) if path else fname
                    s3key = bucket.add(fileinfo['body'],key=s3KeyName)
                    result[key]={
                        "name": fname,
                        "key": s3key
                    }
                    if self.thumb_size:
                        img = Image.open(io.BytesIO(fileinfo['body']))
                        img.thumbnail(self.thumb_size)
                        img_io = io.BytesIO()
                        img.save(img_io,fType)
                        img_io.seek(0)
                        s3ThumbKeyName = "{}/thumbnail/{}{}".format(path,fActual,fExt) if path else "thumbnail/{}{}".format(fActual,fExt)
                        thumb_key = bucket.add(img_io.read(),key=s3ThumbKeyName)
                        result[key]["thumb"] = thumb_key
                    
            self.write({"result":result})
        except Exception as ex:
            logging.exception(path)
            self.write({"error":str(ex)})
            
            