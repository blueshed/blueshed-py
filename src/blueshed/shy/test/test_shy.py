'''
Created on 16 Dec 2013

@author: peterb
'''
import unittest
from blueshed.shy.shy import Shy
from blueshed.shy.worker import Worker


class Test(unittest.TestCase):


    def setUp(self):
        self.shy = Shy()


    def tearDown(self):
        pass


    def testBlank(self):
        def broadcast_(*args):
            self.assertEquals(args,("foo",None))
        self.shy.subscribe(broadcast_)
        
        self.shy.broadcast("foo")
        
        self.shy.unsubscribe(broadcast_)


    def testName(self):
        options = {Shy.QUEUE:"bar"}
        def broadcast_(*args):
            self.assertEquals(args,("foo",options))
        self.shy.subscribe(broadcast_,"bar")
        
        self.shy.broadcast("foo",options)
        
        self.shy.unsubscribe(broadcast_,"bar")



    def testWork(self):
        options = {Shy.QUEUE:"bar"}
        
        class Worker_(Worker):
            def broadcast_(*args):
                self.assertEquals(args,("foo",options))
                
        work = Worker_()
        self.shy.subscribe(broadcast_,"bar")
        
        self.shy.broadcast("foo",options)
        
        self.shy.unsubscribe(broadcast_,"bar")



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()