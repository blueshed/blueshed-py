'''
The minimum Person, Permission for access mixin - inlcude in
you model and mixin in access control

Created on 16 Jul 2014

@author: peterb
'''

from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from blueshed.model_helpers.base import Base



person_permissions_permission = Table('person_permissions_permission', Base.metadata,
    Column('permissions_id', Integer, ForeignKey('person.id')),
    Column('permission_id', Integer, ForeignKey('permission.id')),
    mysql_engine='InnoDB')


class Permission(Base):
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Person(Base):
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    _password = Column(String(255))
    permissions = relationship('Permission',
        primaryjoin='Person.id==person_permissions_permission.c.permissions_id',
        secondaryjoin='Permission.id==person_permissions_permission.c.permission_id',
        secondary='person_permissions_permission',
        lazy='joined')
