'''
Created on 8 Jul 2015

@author: peterb
'''
from blueshed.model_helpers.access_mixin import Access
from blueshed.model_helpers.base_control import BaseControl
from blueshed.model_helpers.fetch_and_carry_mixin import FetchAndCarryMixin
from blueshed.model_helpers import utils
from examples.simple import model
import functools
from blueshed.utils.status import Status
from sqlalchemy.sql.expression import select


class Control(BaseControl,Access,FetchAndCarryMixin):
    
    def __init__(self, db_url, echo=False, pool_recycle=None, drop_all=False):
        BaseControl.__init__(self, db_url, echo, pool_recycle)
        
        if drop_all is True:
            with self.session as session:
                utils.drop_all(session)
            utils.create_all(model.Base, self._engine)
            if drop_all==True:
                with self.session as session:
                    user_permission = model.Permission(name="user")
                    admin = model.Person(email="admin",_password="admin",_token="--foo-bar--")
                    session.add(admin)
                    admin.permissions.append(model.Permission(name="admin"))
                    admin.permissions.append(user_permission)
                    admin.permissions.append(model.Permission(name="api"))
                    
                    user = model.Person(email="user",_password="user")
                    session.add(user)
                    user.permissions.append(user_permission)
                    
                    session.commit()
        
        # initialize after db created
        FetchAndCarryMixin.__init__(self, model)
        self._status = Status(functools.partial(self._broadcast,'_service_status_'))

    
    def begin_web_session(self, accl, client, ip_address, headers):
        if accl:
            with self.session as session:
                user = session.query(model.Person).get(accl)
                self._clients.append(client)
                self._status['clients']=list(set(client.current_user for client in self._clients)) 
                result = self._fc_serialize(user)
                result["permissions"] = [p.name for p in user.permissions]
                return result                    
                
        
    def end_web_session(self, client):
        self._clients.remove(client)
        self._status['clients']=list(set(client.current_user for client in self._clients))


    def echo(self, accl, message):
        self._broadcast("echo",message)
    
        
    def describe(self, accl):
        return self._fc_description
    
    
    def people_report(self, accl):
        with self.session as session:
            q = session.query(model.PersonReport)
            values = [row._asdict() for row in q]
            types = [(col.name,col.type) for col in q.statement.columns]
            return types,values

