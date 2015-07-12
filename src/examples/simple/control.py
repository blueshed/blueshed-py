'''
Created on 8 Jul 2015

@author: peterb
'''
from pkg_resources import resource_filename  # @UnresolvedImport
from blueshed.model_helpers.access_mixin import Access
from blueshed.model_helpers.base_control import BaseControl
from blueshed.model_helpers.fetch_and_carry_mixin import FetchAndCarryMixin
from blueshed.model_helpers import utils
import examples.simple.model as replaceable_model
import examples.simple.model_ext as model
import functools
from blueshed.utils.status import Status
from sqlalchemy.sql.expression import select
import inspect
import os


class Control(BaseControl,Access,FetchAndCarryMixin):
    
    def __init__(self, db_url, echo=False, pool_recycle=None, drop_all=False):
        BaseControl.__init__(self, db_url, echo, pool_recycle)
        
        if drop_all is True:
            with self.session as session:
                utils.drop_all(session)
        
        utils.create_all(model.Base, self._engine)
            
        with self.session as session:
            if session.query(model.Permission).get(1) is None:
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
        FetchAndCarryMixin.__init__(self, model,broadcast_depth=1)
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

        
    def save_model(self, accl, json_model, sqla_model):
        with open("model.json","w") as file:
            file.write(json_model)
        model_path = os.path.join(os.path.dirname(inspect.getfile(replaceable_model)),"model.py")
        with open("model.py.bak","wb") as pybackup:
            with open(model_path,"rb") as pymodel:
                pybackup.write(pymodel.read())
#         should be a callback to main loop!
        with open(model_path,"w") as pymodel:
            pymodel.write(sqla_model)
            
            
    def fetch_model(self, accl):
        if os.path.isfile("model.json"):
            with open("model.json","r") as file:
                return file.read()
        
            
    