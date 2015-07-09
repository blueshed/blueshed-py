'''
Created on Nov 2, 2013

@author: peterb
'''
import logging  # @UnresolvedImport
import tornado.ioloop
from blueshed.fling.fling_rpc import FlingRPC
from blueshed.fling.constants import LOG_FORMAT

class Funcs():
    
    def add(self,a,b):
        return a+b
    
    def subtract(self,a,b):
        return a-b
    
    
class TestClient(FlingRPC):
    
    def on_open(self):
        FlingRPC.on_open(self)
        self.request_response("add",a=2,b=2).\
             add_done_callback(self.done)
             
    def on_close(self, error):
        if error:
            logging.warn(error)
        
        
    def done(self, future):
        logging.info("result: %s - %s",future.result(),future.exception())
        tornado.ioloop.IOLoop.instance().stop()
        
        
    def listen(self, message, options=None):
        logging.info("received: %r",message)
        tornado.ioloop.IOLoop.instance().stop()


def main():
    client = TestClient(Funcs())
    tornado.ioloop.IOLoop.instance().start()
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format=LOG_FORMAT)
    main()
    logging.info("closed")