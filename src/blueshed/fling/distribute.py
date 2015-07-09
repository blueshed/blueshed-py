'''
Created on Oct 30, 2012

@author: peterb
'''
import logging
import multiprocessing
import copy
import time
import inspect
import threading

logging_format ="[%(levelname)1.1s %(asctime)s %(process)d %(thread)x  %(module)s:%(lineno)d] %(message)s"

def sync(func):
    ''' This annotation tells the server to perform this function only when all others a done for this obj '''
    def _expose(f):
        if not hasattr(f, 'crazy_sync_'):
            f.crazy_sync_ = True
        return f

    if func is not None:
        return _expose(func)
    else:
        return _expose

def local(func):
    ''' This annotation tells the server to perform in its own thread, locally '''
    def _expose(f):
        if not hasattr(f, 'crazy_local_'):
            f.crazy_local_ = True
        return f

    if func is not None:
        return _expose(func)
    else:
        return _expose


class _Process(object):
    """Wraps an objects public callables and schedules the server to call methods"""
    def __init__(self, server, obj, method_name, sync_):
        self._method_name = method_name
        self._obj = obj 
        self._server = server
        self._sync = sync_
        
    def __getstate__(self):
        odict = self.__dict__.copy()
        if "_server" in odict:
            odict['_server']=None
        return odict
        
    def __call__(self, *args, **kwargs):
        """call the server to do this"""
        if self._server:
            return self._server._begin(None, self._obj, self._method_name, self._sync, *args, **kwargs)
        else:
            method = getattr(self._obj.__class__, self._method_name)
            return method.__call__(self._obj,*args,**kwargs)
        
    def __repr__(self):
        return '<process %r %s>' % (self._method_name, id(self._obj))



def _runner(process_id, obj, method, args=(), kwargs={}):
    ''' Runs the method on obj and returns the result and error '''
    result = error = None
    try:
        result = getattr(obj,method)(*args,**kwargs)
    except Exception as ex:
        error = str(ex)
        logging.warn(ex)
    logging.debug("ran %s %s",method,obj)
    return process_id, obj, result, error


class Server(object):
    """Acts as a resource pool that can distribute the calls to methods of an object"""
    
    def __init__(self, pool_size=4):
        self.last_process_id = 0
        self.working = {}
        self.waiting = []
        self.results = {}
        self.semaphores = {}
        self.pool = multiprocessing.Pool(pool_size)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(logging_format)
        handler.setFormatter(formatter)
        logger = multiprocessing.get_logger()
        logger.addHandler(handler)
        
        
    def close(self):
        while self.working and self.waiting:
            time.sleep(0.05)
        self.pool.close()
        self.pool.join()
        
        
    def wait(self, process_id=None):
        s = threading.Semaphore(0)
        self.semaphores[process_id if process_id is not None else self.last_process_id] = s
        logging.debug('aquired %s', process_id)
        s.acquire()
        logging.debug('released %s', process_id)
        
        
    def avail(self, obj):
        ''' Wrap the public methods of obj to call CrazyServer - ignore @local annotated methods '''
        for attr in [a for a in dir(obj) if a[0] != '_' and inspect.ismethod(getattr(obj,a))]:
            method = getattr(obj,attr)
            if hasattr(method, "crazy_local_"): 
                continue
            tw = _Process(self, obj, attr, hasattr(method,'crazy_sync_'))
            setattr(obj, attr, tw)
        return obj

        
    def _begin(self, process_id, obj, method_name, sync, *args, **kwargs):
        if process_id is None:
            self.last_process_id = self.last_process_id +1
            process_id = self.last_process_id
        if sync is True and obj in self.working.values():
            self.waiting.append((process_id, obj, method_name, sync, args, kwargs))
        else:
            self.working[process_id]=obj
            obj = copy.deepcopy(obj)
            self.pool.apply_async(_runner,(process_id, obj, method_name, args, kwargs),{},
                                  self._end)
        return process_id
    
    
    def _end(self, cbresult):
        ended_process_id, remote_obj, result, error = cbresult
        self.results[ended_process_id]=(result,error)
        obj = self.working[ended_process_id]
        if error is None:
            for name,rattr in inspect.getmembers(remote_obj):
                if name[0] == "_" or callable(rattr): continue
                lattr = getattr(obj, name) if hasattr(obj, name) else None
                if lattr is None:
                    setattr(obj, name, rattr)
                elif isinstance(lattr, dict) and rattr is not None:
                    for key,value in rattr.items():
                        lattr[key]=value
                else:
                    logging.debug('updated %s %s',name,rattr)
                    setattr(obj, name, rattr)

        del self.working[ended_process_id]
        if obj not in self.working.values():
            for item in self.waiting:
                process_id, instance, method_name, sync, args, kwargs = item
                if obj == instance:
                    self.waiting.remove(item)
                    logging.debug("waking %s", instance)
                    self._begin(process_id,instance,method_name,sync,*args,**kwargs)
                    break
        s = self.semaphores.get(ended_process_id)
        if s:
            del self.semaphores[ended_process_id]
            logging.debug('releasing %s',ended_process_id)
            s.release()
            

    

    
    
    
    