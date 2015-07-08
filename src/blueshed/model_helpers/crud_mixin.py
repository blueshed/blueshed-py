'''
Crub Mixin has been superceded by fetch_and_carry mixin

Created on 2 Jul 2014

@author: peterb
'''
from blueshed.model_helpers import base
from collections import OrderedDict
from decimal import Decimal
from sqlalchemy.inspection import inspect
import logging



class Crud(object):
    
    def __init__(self, model):
        self._model_ = model
    
    
    def fetch(self, accl, type, id=None, attr=None, fkey=None, filter=None, limit=None, offset=None):
        with self.session as session:
            type_ = getattr(self._model_,type)
            query = session.query(type_)
            if id:
                return self.serialize(query.get(id))
            elif attr is not None:
                attr_= getattr(type_,attr)
                if fkey is not None:
                    query = query.filter(attr_==fkey)
                else:
                    query = query.filter(attr_.like("{}%%".format(filter)))
                    query = query.order_by(attr_)
                return {
                    "rows": [self.serialize(item) for item in query] 
                }
            else:
                total = query.count()
                limit_query = query.limit(limit or 10).offset(offset or 0)
                return {
                        "total": total,
                        "rows": [self.serialize(item) for item in limit_query] 
                       }
                
                
    def save(self, accl, item):
        with self.session as session:
            type_ = getattr(self._model_,item["_type"])
            id_ = item["id"]
            if id_:
                obj = session.query(type_).get(abs(id_))
                if id_ < 0:
                    session.delete(obj)
                    session.commit()
                    self._broadcast_on_success("deleted",{"id": id_, "type_": item["_type"]})
                else:
                    self.serialize(obj,item)
                    session.commit()
                    self._broadcast_on_success("updated", self.serialize(obj))
            else:
                obj = type_()
                session.add(obj)
                self.serialize(obj,item)
                session.commit()
                self._broadcast_on_success("added", self.serialize(obj))
                return {"added": {"id": obj.id, "type_": item["_type"]}}
        
    
    
    def serialize(self, obj, from_obj=None):
        if from_obj is not None:
            description_ = self._description_[obj.__class__.__name__]
            for key,value in from_obj.items():
                if key[0] == "_" and key != "id": continue
                attr_ = description_["properties"].get(key)
                if attr_ is not None:
                    logging.info("set %s:%r",key,value)
                    if value is not None and attr_["type"] == "Numeric":
                        setattr(obj,key,Decimal(value))
                    else:
                        setattr(obj,key,value)
        else:
            result = OrderedDict()
            result["_type"]=obj.__class__.__name__
            for key in obj.__mapper__.c.keys():
                if key[0] != "_":
                    result[key] = getattr(obj, key)
            return result


    def _properties_of_(self, cls):
        b = inspect(cls)
        pk = b.primary_key[0]
        result = OrderedDict()
        result[pk.name]=OrderedDict([
                 ("name", pk.name), 
                 ("attr", "pk"),
                 ("type", pk.type.__class__.__name__),
                 ("read_only", True),
                 ("doc", pk.doc)
                 ])
        for key in b.column_attrs.keys():
            if key == pk.name or  key[0] == "_": continue
            attr = b.column_attrs[key]
            p = OrderedDict([
                 ("name", key), 
                 ("attr", "column"),
                 ("type", attr.columns[0].type.__class__.__name__),
                 ("read_only", False),
                 ("fkey", len(attr.columns[0].foreign_keys) > 0),
                 ("doc", attr.doc)
                 ])
            result[key]= p
        for key in b.synonyms.keys():
            if key[0] == "_": continue
            attr = b.synonyms[key]
            p = OrderedDict([
                 ("name", key), 
                 ("attr", "synonym"),
                 ("type", attr.name.type.__class__.__name__),
                 ("read_only", True),
                 ("doc", attr.doc)
                 ])
            result[key]= p
        for key in b.relationships.keys():
            if key[0] == "_": continue
            attr = b.relationships[key]
            direction = attr.direction.name
            fkey = None
            if direction == "MANYTOONE":
                fkey = list(attr.local_columns)[0].name
            elif direction == "ONETOMANY":
                fkey = list(attr.remote_side)[0].name
            p = OrderedDict([ 
                 ("name", key),  
                 ("attr", "relation"),
                 ("direction", direction),
                 ("type", attr.mapper.class_.__name__),
                 ("fkey", fkey),
                 ("doc", attr.doc)
                 ])
            result[key]= p
        for key in b.all_orm_descriptors.keys():
            if key in result.keys() or key[0] == "_": continue
            attr = b.all_orm_descriptors[key]
            p = OrderedDict([
                 ("name", key), 
                 ("attr", "hybrid"),
                 ("type", None),
                 ("read_only", True),
                 ("doc", None)
                 ])
            result[key]= p
        return pk.name, result
    
        
    def describe(self, accl):
        result = {}
        for name, cls in base.Base._decl_class_registry.items():  # @UndefinedVariable
            if name[0] != "_":
                pk, properties = self._properties_of_(cls)
                result[name] = OrderedDict([
                               ("name", name),
                               ("pk", pk),
                               ("properties", properties)
                               ])
        return result