'''
Created on 8 Jul 2015

@author: peterb
'''

from blueshed.model_helpers.access_model import Person, Permission,\
    person_permissions_permission
from blueshed.model_helpers.base import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String


"""
    Because the library requires attributes in Person and Permission
    you can extend them like this:
"""

Person.token = Column(String(80))