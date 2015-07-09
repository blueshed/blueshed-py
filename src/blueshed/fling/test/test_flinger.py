'''
Created on Nov 2, 2013

@author: peterb
'''
import unittest  # @UnresolvedImport
from blueshed.fling.flinger import Flinger
from blueshed.fling.listener import Listener
from blueshed.fling.request import Request


class Test(unittest.TestCase):


    def setUp(self):
        self.flinger=Flinger()

    def testSimple(self):
        sent = "hello world"
        class L(Listener):
            def listen(self, message, options=None):
                self.recieved = message
        listener = L()
        self.flinger.subscribe(listener)
        self.flinger.broadcast(sent)
        self.assertEquals(sent,listener.recieved)


    def testUnsubscribe(self):
        sent = "hello world"
        class L(Listener):
            def listen(self, message, options=None):
                self.recieved = message
        listener = L()
        self.flinger.subscribe(listener,"foo")
        self.flinger.unsubscribe(listener)
        self.flinger.broadcast(sent)
        self.assertEquals(sent,listener.recieved)
        self.flinger.unsubscribe(listener,"foo")
        listener.recieved = None
        self.flinger.broadcast(sent)
        self.assertEquals(None,listener.recieved)


    def testTopicByName(self):
        sent = "hello world"
        class L(Listener):
            def listen(self, message, options=None):
                self.recieved = message
        listener = L()
        self.flinger.subscribe(listener, "foo")
        self.flinger.broadcast(sent)
        self.assertEquals(sent,listener.recieved)
        listener.recieved = None
        self.flinger.broadcast(sent, {"topic":"foo"})
        self.assertEquals(sent,listener.recieved)
        
        listener.recieved = None
        self.flinger.broadcast(sent, {"topic":"bar"})
        self.assertEquals(None,listener.recieved)


    def testQueueByName(self):
        sent = "hello world"
        class L(Listener):
            recieved = None
            def listen(self, message, options=None):
                self.recieved = message
        listener = L()
        listener2 = L()
        self.flinger.subscribe(listener, "foo")
        self.flinger.subscribe(listener2, "foo")
        self.flinger.broadcast(sent, {"queue":"foo"})
        self.assertEquals(sent,listener.recieved)
        self.assertEquals(None,listener2.recieved)


    def testRequest(self):
        request = Request("foo")
        class L(Listener):
            recieved = None
            def listen(self, message, options=None):
                self.recieved = message
                message.result = "bar"
        listener = L()
        listener2 = L()
        self.flinger.subscribe(listener, "foo")
        self.flinger.request_response(request)
        self.assertEquals(request,listener.recieved)
        self.assertEquals("bar",request.result)
        self.assertEquals(None,listener2.recieved)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()