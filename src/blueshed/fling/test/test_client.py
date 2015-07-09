'''
Created on Nov 2, 2013

@author: peterb
'''
import tornado.ioloop
from blueshed.fling.fling_client import FlingClient


class TestClient(FlingClient):
    
    def on_open(self):
        self.subscribe("foo")
        print("subscribed.")
        
        self.broadcast("bar")
        print("sent...")
        
        
    def listen(self, message, options=None):
        print("received: %r" % message)
        tornado.ioloop.IOLoop.instance().stop()


def main():
    client = TestClient()
    tornado.ioloop.IOLoop.instance().start()
    
    
if __name__ == '__main__':
    main()
