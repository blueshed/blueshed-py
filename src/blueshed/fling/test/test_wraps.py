'''
Created on 27 Nov 2013

@author: peterb
'''
import unittest
import functools


class Foo(object):
    
    name = 'foo'
    
    def print(self):
        print(self.name,"Foo")
        
        
class Bar(object):
    
    name = 'bar'
    
    def __init__(self):
        self.foo = Foo()
        self.foo.print = self.print
    
    def print(self):
        print(self.name,"bar")


class Test(unittest.TestCase):


    def testName(self):
        bar = Bar()
        bar.print()
        bar.foo.print()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()