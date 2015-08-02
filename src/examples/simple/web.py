'''
Simple authenticated tornado with knockout,rest and websockets

Created on 8 Jul 2015

@author: peterb
'''
from pkg_resources import resource_filename  # @UnresolvedImport
from tornado.options import options, define, parse_command_line,\
    parse_config_file
import tornado.ioloop
import tornado.web
import logging
import os


from blueshed.utils.utils import patch_tornado, AWSConfig
from examples.simple.control import Control
from blueshed.handlers.login_handler import LoginHandler
from blueshed.handlers.logout_handler import LogoutHandler
from blueshed.handlers.index_handler import IndexHandler
from blueshed.handlers.websocket_handler import WebsocketHandler
from blueshed.handlers.auth_rest_handler import RestHandler
from blueshed.handlers.config_handler import ConfigHandler
from blueshed.handlers.s3upload_direct_handler import S3UploadDirectHandler


define("port", 8080, int, help="port to listen on")
define("debug", default='no', help="debug yes or no - autoreload")
define("db_url", default='sqlite:///simple.db', help="database url")

define("google_key", default="AIzaSyDLLK3zM_Qbe2EbslOtSHGA-PwyVla0T0Y", help="enable use of google-maps")

define("aws_access_key_id", "AKIAJXC7YLZHVXMKNPJA", help="aws access key")
define("aws_secret_access_key", "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", help="aws secret access key")
define("upload_bucket_region","eu-west-1", help="where is the bucket")
define("upload_bucket", "blueshed-notes", help="default image s3 bucket name")

patch_tornado()

WS_VERSION = 1

def main():
    config_path = "simple.conf"
    if os.path.isfile(config_path):     
        logging.info("loading config file")       
        parse_config_file(config_path)
    
    parse_command_line()

    s3_config = AWSConfig(options.aws_access_key_id,
                          os.environ.get("S3_CONFIG",
                          options.aws_secret_access_key))
    
    ws_config = {
        "google_key": options.google_key,
        "aws_access_key_id": options.aws_access_key_id,
        "aws_secret_access_key": options.aws_secret_access_key,
        "s3_bucket_region": options.upload_bucket_region,
        "s3_bucket": options.upload_bucket,
        "s3_base_url": "//" + options.upload_bucket + ".s3.amazonaws.com",
        "s3_upload_url": "/images/"
    }
    
    port = int(os.environ.get("PORT", options.port))
    db_url = os.environ.get("CLEARDB_DATABASE_URL",options.db_url)
                    
    control = Control(db_url=db_url,drop_all=True)
    
    handlers = [
        (r"/websocket", WebsocketHandler),
        (r"/login(.*)", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/config", ConfigHandler, {"config": ws_config }),
        (r"/rest/(.*)", RestHandler,{"auth_header":'simple-auth-token'}),
        (r"/images/(.*)", S3UploadDirectHandler, {
            "bucket": options.upload_bucket,
            "s3_config": s3_config
            }),
        (r"/", IndexHandler),
    ]
    settings = {
        "static_path": resource_filename('examples.simple',"www/static"),
        "template_path": resource_filename('examples.simple',"www/templates"),
        "cookie_secret": 'blueshed.simple-secret',
        "cookie_name": 'blueshed.simple-user',
        "login_url": '/login',
        "gzip": True,
        "control": control,
        "ws_version": WS_VERSION,
        "ws_config": ws_config,
        "debug": options.debug
    }
    
    application = tornado.web.Application(handlers, **settings)
    application.listen(port)
    logging.info("listening on port {}".format(port))
    logging.info("mode:{}".format("production" if options.debug=='no' else 'debug'))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
