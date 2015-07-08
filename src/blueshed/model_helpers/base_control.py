'''
Base control provides support for websocket clients and
transaction based broadcasting of events


Created on 21 Oct 2014

@author: peterb
'''
from blueshed.model_helpers import utils


class BaseControl(object):


    def __init__(self, db_url,echo=False,pool_recycle=None):
        '''
        Constructor
        '''
        self._clients = []
        self._pending = []
        self._engine, self._Session = utils.connect(db_url,echo,pool_recycle)
        
    
    def _broadcast(self, signal, message, accl=None):
        if accl:
            for client in self._clients:
                if client.current_user in accl:
                    client.broadcast({"signal":signal, "message":message})
        else:
            for client in self._clients:
                client.broadcast({"signal":signal, "message":message})
        
    
    def _broadcast_on_success(self, signal, message, accl=None):
        self._pending.append((signal,message,accl))
        
         
    def _broadcast_result_(self, signal, message, accl=None):
        self._broadcast_on_success(signal,message,accl)
        return message    
            
            
    def _flush(self, err=None):
        if err is None:
            for args in self._pending:
                self._broadcast(*args)
        self._pending = []
        

    @property
    def session(self):
        ''' 
            returns a self closing session for use by with statements 
        '''
        session = self._Session()
        class closing_session:
            def __enter__(self):
                return session
            def __exit__(self, type, value, traceback):
                session.close()
        return closing_session()
    
    
    def user_session(self, accl):
        ''' 
            returns a self closing session for use by with statements 
            associating the action accl to the audit listener
        '''
        session = self._Session()
        audit = self._audit
        class closing_session:
            def __enter__(self):
                audit.accl_key = accl
                return session
            def __exit__(self, type, value, traceback):
                audit.accl_key = None
                session.close()
        return closing_session()
    
    
    def ping(self, accl):
        # respond to keep alive ping
        return "pong"