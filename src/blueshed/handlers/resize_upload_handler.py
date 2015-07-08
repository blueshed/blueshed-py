'''
Created on Jan 4, 2013

@author: peterb
'''
from tornado.web import StaticFileHandler
from tornado.escape import url_unescape
import logging
import os

from PIL import Image
from PIL.ExifTags import TAGS
from blueshed.utils.resize_and_crop import resize_and_crop


class ResizeUploadHandler(StaticFileHandler):
    """
        Uses pillow to thumbnail an uploaded file
        to a local directory
    """
    
    def initialize(self, path, default_filename=None):
        self.check_dir(path)
        StaticFileHandler.initialize(self, path, default_filename)
        
        
    def check_dir(self, path):
        if not os.path.isdir(path):
            logging.info("creating upload directory %s", path)
            os.makedirs(path)
            
        thumb_path = os.path.join(path,"thumbnails")
        if not os.path.isdir(thumb_path):
            logging.info("creating thumbnail directory %s", thumb_path)
            os.makedirs(thumb_path)
        
    
    @classmethod
    def get_exif(cls, fn):
        ret = {}
        i = Image.open(fn)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret

    @classmethod
    def get_lat_long(cls, fn):
        try:
            a = cls.get_exif(fn)
            lat = [float(x)/float(y) for x, y in a['GPSInfo'][2]]
            latref = a['GPSInfo'][1]
            lon = [float(x)/float(y) for x, y in a['GPSInfo'][4]]
            lonref = a['GPSInfo'][3]
            
            lat = lat[0] + lat[1]/60 + lat[2]/3600
            lon = lon[0] + lon[1]/60 + lon[2]/3600
            if latref == 'S':
                lat = -lat
            if lonref == 'W':
                lon = -lon
                
            return lat,lon
        except (KeyError,AttributeError):
            return None
        
    
    def make_sm(self, root, file_name):
        path = os.path.join(root,file_name)
        thumb_path = os.path.join(root,"thumbnails",file_name)
        try:
            size = 184, 138
            resize_and_crop(path, thumb_path, size, "middle")
        except:
            logging.exception(path)
            pass
        

    def post(self,path=None):
        try:
            result = {}
            root = os.path.join(self.root,path) if path else self.root
            self.check_dir(root)
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
                    logging.info("uploading %s", file_path)
                    with open(file_path,'wb') as fh:
                        fh.write(fileinfo['body'])
                    info = self.get_lat_long(file_path)
                    self.make_sm(root,fname)
                    result[key]={
                                 "name":fname,
                                 "info":info
                                 }
            self.write({"result":result})
        except Exception as ex:
            logging.exception(path)
            self.write({"error":str(ex)})
            
