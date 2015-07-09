'''
Created on Nov 2, 2013

@author: peterb
'''

import logging
import tornado.ioloop
import tornado.web
from blueshed.fling.fling_handler import FlingHandler
from blueshed.fling.flinger import Flinger
from tornado.options import parse_command_line, options, define


define("port",7777,int,help="port to listen on")
define("debug",False,bool,help="dynamic restart etc")


def main(port=None):
    parse_command_line()
    
    port = port if port else options.port
    
    application = tornado.web.Application([
                                           (r"/ws", FlingHandler),
                                           ], 
                                          flinger=Flinger(), 
                                          debug=options.debug)
    application.listen(port)
    logging.info("listening on port %s",port)
    tornado.ioloop.IOLoop.instance().start()
    


if __name__ == "__main__":
    main()