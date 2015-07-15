'''
Created on 12 Jul 2015

@author: peterb
'''
from blueshed.model_helpers.sqla_views import view
from blueshed.model_helpers.sql_extensions import JSONEncodedDict
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql.expression import select, join
from sqlalchemy.sql.functions import func

from examples.simple.model import *
from blueshed.model_helpers.access_model import Person, Permission,\
    person_permissions_permission


Person._token = Column(String(80))
Person._preferences = Column(MutableDict.as_mutable(JSONEncodedDict(255)))
Person.firstname = Column(String(80))
Person.lastname = Column(String(80))
Person.photo = Column(String(128))

'''
    An example View
'''
q = select([Person.id.label('id'), 
            Person.email.label('email'),
            func.count(Permission.id).label('permission_count')]).\
            select_from(join(Person,
                             person_permissions_permission,
                             Person.id==person_permissions_permission.c.permissions_id).\
                        join(Permission,
                             Permission.id==person_permissions_permission.c.permission_id)).\
            group_by(Permission.id)

PersonReport = view("person_report", Base.metadata, q)
                        
