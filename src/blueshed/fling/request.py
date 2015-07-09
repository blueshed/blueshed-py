'''
Created on Nov 2, 2013

@author: peterb
'''


class Request(object):
    
    def __init__(self, name, options=None, callback=None, request_id=None):
        self.name = name
        self.options = options
        self.request_id = request_id
        self._callback = callback
        self._handled = False
        self._result = None
        self._error = None
        
    def cancel(self):
        self._callback = None

    @property
    def handled(self):
        return self._handled
            
    @handled.setter
    def handled(self, value):
        self._handled = value

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.handled = True
        if self._callback:
            self._callback(self)

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value
        self.handled = True
        if self._callback:
            self._callback(self)
            
    def __str__(self):
        return "request:{}[{}]".format(self.name, self.request_id)
        