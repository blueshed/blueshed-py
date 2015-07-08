'''
Support for multi-processing using python process pools in
Tornado.

Created on 8 Jun 2015

@author: peterb
'''
from multiprocessing import Pool  # @UnresolvedImport
from tornado.log import enable_pretty_logging
import logging
import os
from blueshed.model_helpers import model_utils
from tornado.ioloop import IOLoop
import functools


_session_ = None
_engine_ = None
def pool_init(db_url,db_echo=False,db_pool_recycle=None):
    global _session_, _engine_
    enable_pretty_logging()
    _engine_, _session_ = model_utils.connect(db_url,db_echo,db_pool_recycle)
    logging.info("pool connected %s",os.getpid())
    
    
def get_session():
    session = _session_()
#     try:
#         session.connection().connection.ping()
#     except:
#         logging.exception()
#         pass
    class closing_session:
        def __enter__(self):
            return session
        def __exit__(self, _type, _value, _traceback):
            session.close()
    return closing_session()


def get_pool(count,db_url,db_echo=False,db_pool_recycle=None):
    return Pool(count,initializer=pool_init,initargs=(db_url,db_echo,db_pool_recycle))



def run_callback(callback,result):
    IOLoop.instance().add_callback(callback,result)


def pool_call(pool, f,callback,*args,**kwargs):
    pool.apply_async(f,args=args,kwds=kwargs,
                     callback=functools.partial(run_callback,callback))
    
    