'''
Created on 2 Jul 2014

@author: peterb
'''
import blueshed.model_helpers.access_model as model
from sqlalchemy.sql.expression import and_
import logging

class Access(object):
    """
        Provides a mixin to support authentication
    """

    # ACCESS CONTROL
    
    def login(self, email, password):
        with self.session as session:
            user = session.query(model.Person).filter(and_(model.Person.email==email,
                                                           model.Person._password==password)).first()
            if user is None:
                raise Exception("Email or password incorrect!")
            
            return str(user.id)
        
        
    def forgotten_password(self, accl, email):
        with self.session as session:
            user = session.query(model.Person).filter(model.Person.email==email).first()
            if user is None:
                raise Exception("No such user")
            self._email_password_(email, user._password)
            
            
    def get_token_user(self, token):
        with self.control.session as session:
            user = session.query(model.Person).filter_by(_token=token).first()
            if user is not None and "api" in [p.name for p in user.permissions]:
                user.serialize
        
        
    def register(self, accl, email):
        if accl is not None:
            raise Exception("cannot register another user.")
        if len(email) < 6 or "@" not in email or "." not in email:
            raise Exception("Email invalid")
        with self.session as session:
            password = self.generate_password()
            user = model.Person(email=email,
                                _password=password)
            session.add(user)
            session.commit()
            self._email_password_(email, password)
            logging.debug("registered %s", email)

            return True
        
        
    def change_password(self, accl, old_password, new_password):
        with self.session as session:
            accl_user = session.query(model.Person).get(accl)
            if old_password != accl_user._password:
                raise Exception("old password does not match")
            accl_user._password = new_password
            session.commit()
            return True


    def get_user(self, user_id):
        if user_id is None: return
        with self.session as session:
            user = session.query(model.Person).get(user_id)
            return user.serialize
        
    
    def add_user(self, details):
        with self.session as session:
            user = model.Person(email=details.get("email"),
                                _password=details.get("password"))
            session.add(user)
            for permission_name in details.get("permissions"):
                permission = session.query(model.Permission).\
                                     filter(model.Permission.name==permission_name).first()
                if permission is None:
                    raise Exception("No such permission {}".format(permission_name))
                user.permissions.append(permission)
            session.commit()
            return self.json_user(user)

    
    def save_user(self, details):
        pass
    
    
    def _require_permission_(self, session, accl, permissions):
        user = session.query(model.Person).get(accl)
        for permission in user.permissions:
            if permission.name in permissions:
                return True
        raise Exception("{} does not have permissions:{}",user.email,permissions)