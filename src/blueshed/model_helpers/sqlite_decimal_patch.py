'''
Created on Oct 25, 2012

@author: peterb
'''
import sqlalchemy.types as types
from sqlalchemy.interfaces import PoolListener 
from decimal import getcontext

def use_decimals():
    class SqliteNumeric(types.TypeDecorator):
        impl = types.TypeEngine
        def load_dialect_impl(self, dialect):
            return dialect.type_descriptor(types.VARCHAR(100))
        def process_bind_param(self, value, dialect):
            if value:
                return str(value)
        def process_result_value(self, value, dialect):
            if value:
                return getcontext().create_decimal(value)
    
    # can overwrite the imported type name
    # @note: the TypeDecorator does not guarantie the scale and precision.
    # you can do this with separate checks
    types.Numeric = SqliteNumeric


class SetTextFactory(PoolListener): 
    def connect(self, dbapi_con, con_record): 
        dbapi_con.text_factory = str 
        
