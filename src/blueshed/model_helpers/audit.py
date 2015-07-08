'''
Audit is the persistent log of crud activity

Created on Sep 27, 2011

@author: peterb
'''
from sqlalchemy.schema import Column, Index
from sqlalchemy.types import Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import synonym
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm.attributes import PASSIVE_NO_FETCH
from sqlalchemy.orm.interfaces import MANYTOMANY
from blueshed.model_helpers.base import Base
from blueshed.utils import utils
import datetime


class Audit(Base):
    ACTIONS = [u'created',u'updated',u'deleted',u'added',u'removed']
    
    id= Column(Integer, primary_key=True)
    action = Column(Enum(*ACTIONS))
    type = Column(String(80))
    _ref = Column('ref',String(80))
    _data = Column('data',Text())
    _changed = Column('changed',Text())
    attr = Column(String(80))
    _attr_ref = Column('attr_ref',String(80))
    
    mod_user_id = Column(Integer)
    mod_time = Column(DateTime, default=datetime.datetime.now)
    
    def _read_ref(self):
        return utils.loads(self._ref) if self._ref else None
        
    def _write_ref(self, value):
        self._ref = utils.dumps(value)
    
    ref = synonym('_ref', descriptor=property(_read_ref, _write_ref))
    
    def _read_attr_ref(self):
        return utils.loads(self._attr_ref) if self._attr_ref else None
        
    def _write_attr_ref(self, value):
        self._attr_ref = utils.dumps(value)
    
    attr_ref = synonym('_attr_ref', descriptor=property(_read_attr_ref, _write_attr_ref))
    
    def _read_data(self):
        return utils.loads(self._data) if self._data else None
        
    def _write_data(self, value):
        self._data = utils.dumps(value)
    
    data = synonym('_data', descriptor=property(_read_data, _write_data))
    
    def _read_changed(self):
        return utils.loads(self._changed) if self._changed else None
        
    def _write_changed(self, value):
        self._changed = utils.dumps(value)
    
    changed = synonym('_changed', descriptor=property(_read_changed, _write_changed))
    
    @classmethod
    def _get_instance_pk(cls, obj, obj_mapper=None):
        from sqlalchemy.orm import object_mapper
        obj_mapper = obj_mapper or object_mapper(obj)
        result = []
        for om in obj_mapper.iterate_to_root():
            for pk in om.local_table.primary_key:
                result.append(getattr(obj, pk.key))
        return result
    
            
    @classmethod
    def create_version(cls, obj, session, action, mod_user_id=None):
        from sqlalchemy.orm import attributes, object_mapper
        from sqlalchemy.orm.exc import UnmappedColumnError
        from sqlalchemy.orm.properties import RelationshipProperty  # @UnresolvedImport
        
        obj_mapper = object_mapper(obj)
        obj_state = attributes.instance_state(obj)
    
        attr = {}
        changed = {}
    
        obj_changed = False

        if hasattr(obj.__class__, '_no_genoa_audit_'):
            return
            
        for om in obj_mapper.iterate_to_root():
            
            primary_keys = [pk.key for pk in om.local_table.primary_key]
            
            for obj_col in om.local_table.c:    
                # get the value of the
                # attribute based on the MapperProperty related to the
                # mapped column.  this will allow usage of MapperProperties
                # that have a different keyname than that of the mapped column.
                try:
                    prop = obj_mapper.get_property_by_column(obj_col)
                except UnmappedColumnError:
                    # in the case of single table inheritance, there may be 
                    # columns on the mapped table intended for the subclass only.
                    # the "unmapped" status of the subclass column on the 
                    # base class is a feature of the declarative module as of sqla 0.5.2.
                    continue

                if prop.key in primary_keys:
                    attr[prop.key] = getattr(obj, prop.key)
                else:
                    a, u, d = attributes.get_history(obj, prop.key, PASSIVE_NO_FETCH)
                    if d:
                        attr[obj_col.key] = d[0]
                        changed[prop.key] = getattr(obj, prop.key)
                        obj_changed = True
                    elif u:
                        attr[obj_col.key] = u[0]
                    elif a:
                        # if the attribute had no value.
                        attr[obj_col.key] = a[0]
                        changed[prop.key] = getattr(obj, prop.key)
                        obj_changed = True                
    
    
        primary_key = cls._get_instance_pk(obj, obj_mapper)
        if obj_changed is True or action=='deleted':
            hist = cls(action=action,
                       type=obj.__class__.__name__,
                       ref=utils.dumps(primary_key),
                       data=utils.dumps(attr),
                       changed=utils.dumps(changed),
                       mod_user_id=mod_user_id)
            session.add(hist)

        for prop in obj_mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty) and \
                prop.direction == MANYTOMANY and \
                attributes.get_history(obj, prop.key).has_changes():
                a, u, d = attributes.get_history(obj, prop.key, PASSIVE_NO_FETCH)
                for item in a:
                    hist = cls(action='added',
                               type=obj.__class__.__name__,
                               ref=utils.dumps(primary_key),
                               attr=item.__class__.__name__,
                               attr_ref=utils.dumps(cls._get_instance_pk(item)),
                               mod_user_id=mod_user_id)
                    session.add(hist)
                for item in d:
                    hist = cls(action='removed',
                               type=obj.__class__.__name__,
                               ref=utils.dumps(primary_key),
                               attr=item.__class__.__name__,
                               attr_ref=utils.dumps(cls._get_instance_pk(item)),
                               mod_user_id=mod_user_id)
                    session.add(hist)
                    
                    
    @classmethod
    def get_audit_trail(cls, obj):
        from sqlalchemy.orm import object_mapper
        session = object_session(obj)
        obj_mapper = object_mapper(obj)
        primary_key = cls._get_instance_pk(obj, obj_mapper)
        return session.query(cls).filter(and_(cls.type==obj.__class__.__name__,
                                              cls.ref==utils.dumps(primary_key)))
        

# to optimize audit trail query
Index('idx_audit_type_ref', Audit.type, Audit.ref, unique=False)

