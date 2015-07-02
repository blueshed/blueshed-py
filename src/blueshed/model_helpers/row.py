'''
Created on 29 Jun 2015

@author: peterb
'''
from collections import OrderedDict


class Row(OrderedDict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)