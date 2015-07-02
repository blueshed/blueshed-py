'''
Created on 29 Jun 2015

@author: peterb
'''
import logging
from blueshed.model_helpers.row import Row
from sqlalchemy.orm.session import object_session


class SerializeMixin(object):
    
    @property
    def serialize(self):
        return self._to_pairs()        
    
    def _to_pairs(self, ignore=None):
        result = Row()
        result["_type"]=self.__class__.__name__
        for key in self.__mapper__.c.keys():
            if key[0] != "_":
                result[key] = getattr(self, key)
        return result
    
    
    @serialize.setter
    def serialize(self, obj):
        self._from_pairs(obj)
        
    def _from_pairs(self, obj):
        for key in self.__mapper__.c.keys():
            if key[0] == "_" or key in ["id","last_updated"]: continue
            value = obj.get(key)
            logging.debug("set %s:%r",key,value)
            if key == "version_id" and value == None: continue
            setattr(self,key,value)
            
            
    def to_json(self):
        return self._to_pairs()
    
    
    def _from_one_to_many_pairs(self, pairs, key, clazz):
        '''Simple saving of one-to-many relations - not usually associated with from_pairs'''
        added = []
        updated = [] 
        deleted = []
        errors = []
        session = object_session(self)
        for item in pairs.get(key,[]):
            item_id = item.get('id')
            obj = None
            if item_id:
                if int(item_id) < 0:
                    obj = session.query(clazz).get(abs(int(item_id)))
                    session.delete(obj)
                    deleted.append(obj)
                    continue
                else:
                    obj = session.query(clazz).get(item_id)
                    if obj.from_pairs(item) is True:
                        e = obj._validate_()
                        if e:
                            errors.extend(e)
                        updated.append(obj)
            else:
                obj = clazz()
                getattr(self,key).append(obj)
                if obj.from_pairs(item) is True:
                    e = obj._validate_()
                    if e:
                        errors.extend(e)
                    added.append(obj)
        return added, updated, deleted, errors


    def _from_many_to_many_pairs(self, pairs, key, clazz):
        '''Simple saving of many-to-many relations - not usually associated with from_pairs'''
        added = []
        removed = []
        session = object_session(self)
        existing = dict([(a.id,a) for a in getattr(self,key)])
        new_list = dict([(b.get("id"),b) for b in pairs.get(key,[])])
        for to_remove in set(existing.keys()) - set(new_list.keys()):
            obj = existing[to_remove]
            getattr(self,key).remove(obj)
            removed.append(obj)
            logging.info("m2m removed %s",obj)
        for to_add in set(new_list.keys()) - set(existing.keys()):
            obj = session.query(clazz).get(abs(int(to_add)))
            getattr(self,key).append(obj)
            added.append(obj)
            logging.info("m2m added %s",obj)
        return added, removed
    
    
    @classmethod
    def _unique(cls, session, hashfunc=None, queryfunc=None, constructor=None, arg=None, kw=None):
        hashfunc = hashfunc if hashfunc else lambda name: name
        queryfunc = queryfunc if queryfunc else lambda query, name: query.filter(cls.name == name)
        constructor = constructor if constructor else cls
        arg = arg if arg else []
        kw = kw if kw else {}
        cache = getattr(session, '_unique_{}_cache'.format(cls.__tablename__), None)
        if cache is None:
            cache = {}
            setattr(session, '_unique_{}_cache'.format(cls.__tablename__), cache)
    
        key = (cls, hashfunc(*arg, **kw))
        if key in cache:
            return cache[key]
        else:
            with session.no_autoflush:
                q = session.query(cls)
                q = queryfunc(q, *arg, **kw)
                obj = q.first()
                if not obj:
                    obj = constructor(*arg, **kw)
                    session.add(obj)
            cache[key] = obj
            return obj
