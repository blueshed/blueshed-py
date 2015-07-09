
    
'''
Created on Nov 2, 2013

@author: peterb
'''
import logging  # @UnresolvedImport
import pickle  # @UnresolvedImport
import jsonpickle
import tornado.ioloop
from blueshed.fling.fling_client import FlingClient
from blueshed.fling.constants import LOG_FORMAT
from blueshed.fling.test.test_job import TestJob

    
    
class TestClient(FlingClient):
    
    def on_open(self):
        job = TestJob()
        pjob = jsonpickle.encode(job)
        f = self.request_response("pickled_work",obj=pjob,method="sum",args=[2,3])
        logging.info("sent...")
        f.add_done_callback(self.done)
        
        
    def done(self, future):
        try:
            obj = jsonpickle.decode(future.result())
            logging.info("received: %r",obj.result)
        finally:
            tornado.ioloop.IOLoop.instance().stop()


def main():
    client = TestClient()
    tornado.ioloop.IOLoop.instance().start()
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format=LOG_FORMAT)
    main()
    logging.info("closed")