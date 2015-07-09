'''
Created on Nov 2, 2013

@author: peterb
'''

class Listener(object):
    '''
    You do not have to subclass this, 
    duck-typing means use this method signature
    '''
    def listen(self, message, options=None):
        raise Exception("Sub-class responsibility")