'''
Created on Aug 11, 2011

@author: peterb
'''
from random import random
from math import pow, sqrt
from blueshed.fling.distribute import sync, local


class MonteCarloPi(object):
    """Calcuates an approximation for pi using random numbers"""
    
    
    def __init__(self, steps, throws):
        self.steps = steps
        self.throws = throws
        self.hits = {}
        self._step = 0
        self.result = None
        
    def __repr__(self):
        return "<MonteCarloPi steps=%s, throws=%s hits=%r, step=%s, result=%s>" % (self.steps,self.throws, self.hits, self._step, self.result)
        
    @local
    def run(self):
        for i in range(0, self.steps):
            self._step = i
            self.throw()
        self.end()
        
    
    def throw(self):
        """samples one step with random throws into a circle"""
        hits = 0
        for i in range (0, self.throws):
            x = random()
            y = random()
            dist = sqrt(pow(x, 2) + pow(y, 2))
            if dist <= 1.0:
                hits = hits + 1.0
        self.hits[self._step] =  hits
        
    @sync
    def end(self):
        """reduces the sample sets and figures the result"""
        hits = throws = 0.0
        for n in range(0,self.steps):
            hits = hits + float(self.hits[n])
            throws = throws + float(self.throws)
        pi = 4 * (hits / throws)
        self.result = pi
        return self.result
    
    

if __name__ == '__main__':
    import logging
    import time
    from blueshed.fling.distribute import Server
    from blueshed.fling.constants import LOG_FORMAT
    
    logging.basicConfig(level=logging.INFO, 
                        format=LOG_FORMAT)
    logging.info("start")
    start = time.time()
    pi = MonteCarloPi(10,1000000)
    paralell = True
    if paralell is False:
        pi.run()
    else:
        server = Server(4)
        server.avail(pi)
        pi.run()
        server.close()
    
    logging.info("pi: %s %s (secs)", pi.result, time.time() - start)
    
    