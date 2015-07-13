'''
SQLAlchemy support for MySQL rollup

Created on Apr 1, 2013

@author: peterb
'''
from sqlalchemy.sql.expression import ColumnElement, _clause_element_as_expr
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR
from blueshed.utils.utils import dumps, loads


class rollup(ColumnElement):
    def __init__(self, *elements):
        self.elements = [_clause_element_as_expr(e) for e in elements]

@compiles(rollup, "mysql")
def _mysql_rollup(element, compiler, **kw):
    return "%s WITH ROLLUP" % (', '.join([compiler.process(e, **kw) for e in element.elements]))
        

class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = loads(value)
        return value
    
    