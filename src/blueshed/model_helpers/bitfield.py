'''
Created on Feb 23, 2013

@author: peterb
'''

_isiterable_ = lambda obj: isinstance(obj, list)
    
class BitField(object):
    
    def __init__(self, value=0):
        if value is None or _isiterable_(value):
            self.value = 0
        if _isiterable_(value):
            self.value = 0
            for item in value:
                self.set(item)
        else:
            self.value = value
        
    def __getitem__(self, key):
        if key in self._VALUES_:
            bit = self._VALUES_.index(key)
            if ((self.value>>bit) % 2 != 0):
                return self._VALUES_[bit]
        else:
            return self.value & key > 0
        
    def set(self, key):
        bit = self._VALUES_.index(key)
        self.value = self.value | 1<<bit;
            
    def clear(self, key):
        bit = self._VALUES_.index(key)
        self.value = self.value & ~(1<<bit)
        
        
    def to_json(self):
        return self.value
    
    
    def to_list(self):
        result = []
        for bit in range(0,len(self._VALUES_)):
            if ((self.value>>bit) % 2 != 0):
                result.append(self._VALUES_[bit])
        return result
    
    
    def __str__(self):
        return str(self.value)
    
    
    def __repr__(self):
        return repr(self.to_list())
    
    
    @classmethod
    def ALL(cls):
        return cls(cls._VALUES_).value
    
    
