'''
Created on 8 Jul 2015

@author: peterb
'''
from blueshed.model_helpers.access_mixin import Access, requires_permissions
from blueshed.model_helpers.base_control import BaseControl
from blueshed.model_helpers.fetch_and_carry_mixin import FetchAndCarryMixin
from blueshed.model_helpers import utils
import examples.simple.model as replaceable_model
import examples.simple.model_ext as model
import functools
from blueshed.utils.status import Status
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

    
    def _begin_web_session(self, accl, client, ip_address, headers):
        if accl:
            with self.session as session:
                user = session.query(model.Person).get(accl)
                self._clients.append(client)
                self._status['clients']=list(set(client.current_user for client in self._clients)) 
                result = self._fc_serialize(user)
                result["permissions"] = [p.name for p in user.permissions]
                result["prefernces"] = user._preferences
                return result                    
                
        
    def _end_web_session(self, client):
        self._clients.remove(client)
        self._status['clients']=list(set(client.current_user for client in self._clients))


    def echo(self, accl, message):
        """
            Send message to all connected clients with signal:'echo'
        """
        self._broadcast("echo",message)
        return "broadcast to {} clients".format(len(self._clients))
        
    
    @requires_permissions("admin")
    def people_report(self, accl, session):
        """
            Returns a report of people and permission counts
        """
        q = session.query(model.PersonReport)
        values = [row._asdict() for row in q]
        types = [(col.name,str(col.type)) for col in q.statement.columns]
        return types,values
    
    
    def save_prefernces(self, accl, preferences):
        with self.session as session:
            user = session.query(model.Person).get(accl)
            user._preferences = preferences
            session.commit()

        
    @requires_permissions("admin")
    def save_model(self, accl, session, json_model, sqla_model):
        """
            Will change the model and cause a restart
        """
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
        """
            Returns the last stored model.json
        """
        if os.path.isfile("model.json"):
            with open("model.json","r") as file:
                return file.read()
        
            
    