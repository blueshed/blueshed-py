'''
A Simple mixin that inspects your model and provides a
serialize interface to is through two public methods:
    
    fetch - the equivalent of select, get_by_id and get_attribute
    carry - the equivalent of create, update and delete 

Send the _fc_description to the websocket client can enable
a knockout clientside observable model updated by messages
in real-time.

Created on 8 Jul 2015

@author: peterb
'''
import logging
from collections import OrderedDict
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import asc, desc


class FetchAndCarryMixin(object):
    
    def __init__(self, model):
        self._fc_model = model
        self._fc_description = self._fc_describe(model.Base)
    
    
    def fetch(self, accl, type, id=None, attr=None, 
              filter=None, match=None, limit=None, offset=None, 
              order_by=None, order_by_asc=False,
              depth=0):
        with self.session as session:
            type_ = getattr(self._fc_model,type)
            query = session.query(type_)
            if attr is not None:
                attr_= getattr(type_,attr)
                if filter or match:
                    total = query.count()
                    if filter:
                        query = query.filter(attr_.like("{}%%".format(filter)))
                        query = query.order_by(attr_)
                    elif match:
                        query = query.filter(attr==match)
                    filter_total = query.count()
                elif id:
                    obj = query.get(id)
                    query = getattr(obj, attr)
                    if not hasattr(query, '__iter__'):
                        return {
                            "type": type,
                            "id": id,
                            "attr": attr,
                            "type": "single",
                            "value": self._fc_serialize(query,depth=depth)
                        }
                    return {
                        "type": type,
                        "id": id,
                        "attr": attr,
                        "attr_type": "collection",
                        "value": [self._fc_serialize(item, depth=depth) for item in query]
                    }
                limit_query = query.limit(limit or 10).offset(offset or 0)
                return {
                    "type": "collection",
                    "total": total,
                    "filter_total": filter_total,
                    "offset": offset,
                    "limit": limit,
                    "rows": [self._fc_serialize(item, depth=depth) for item in limit_query] 
                }
            elif id:
                return {
                        "type": type,
                        "id": id,
                        "value": self._fc_serialize(query.get(id))
                        }
            else:
                total = query.count()
                if order_by:
                    order_by_ = getattr(self._fc_model,order_by)
                    if order_by_asc is True:
                        query = query.order_by(asc(order_by_))
                    else:
                        query = query.order_by(desc(order_by_))
                limit_query = query.limit(limit or 10).offset(offset or 0)
                return {
                        "total": total,
                        "filter_total": total,
                        "rows": [self._fc_serialize(item) for item in limit_query] 
                       }   
    
    
    def carry(self, accl, item, to_add=None, to_remove=None):
        logging.info(item)
        result = None
        to_broadcast = []
        with self.session as session:
            
            def add_items(obj):
                if to_add:
                    surrogate = {"id": obj.id, "_type": obj.__class__.__name__}
                    for attr, type_, id_ in to_add:
                        item = session.query(getattr(self._fc_model,type_)).get(id_)
                        getattr(obj,attr).append(item)
                        to_broadcast.append("added",{ "target": surrogate, "item":[attr, type_, id_] })
                        
            def remove_items(obj):
                if to_remove:
                    surrogate = {"id": obj.id, "_type": obj.__class__.__name__}
                    for attr, type_, id_ in to_remove:
                        item = session.query(getattr(self._fc_model,type_)).get(id_)
                        getattr(obj,attr).remove(item)
                        to_broadcast.append("removed",{ "target": surrogate, "item":[attr, type_, id_] })
                
            type_ = getattr(self._fc_model,item["_type"])
            id_ = item["id"]
            if id_:
                obj = session.query(type_).get(abs(id_))
                if id_ < 0:
                    message = "deleted {}".format(obj.__class__.__name__)
                    surrogate = {"id": obj.id, "_type": obj.__class__.__name__}
                    session.delete(obj)
                    session.commit()
                    self._broadcast_on_success(message, surrogate)
                    return surrogate
                else:
                    message = "saved"
            else:
                message = "created"
                obj = type_()
                session.add(obj)
            self._fc_serialize(obj,item)
            session.flush()
            add_items(obj)
            remove_items(obj)
            session.commit()
            result = self._fc_serialize(obj)
            signal = "{} {}".format(message,obj.__class__.__name__)
            self._broadcast_on_success(signal, result)
        for signal, message in to_broadcast:
            self._broadcast_on_success(signal, message)
        return result
        
        
    def _fc_serialize(self, item, values=None, depth=0):
        if item:
            meta = next(d for d in self._fc_description if d['name'] == item.__class__.__name__)
            if meta:
                if values:
                    for p in meta['properties'].values():
                        name = p["name"]
                        if name in values and\
                           p.get("read_only") is not True and \
                           p["attr"][0] is not "_" and \
                           p["attr"] in ["column","hybrid"]:
                                value = values[name]
                                logging.info("setting: %s=%r",name,value)
                                setattr(item,name,value)
                else:
                    values = [(n['name'],getattr(item,n['name'])) for n in meta['properties'].values()\
                               if n['attr'][0] is not "_" and n['attr'] in ['column','hybrid','pk']]
                    values.append(("_type",meta['name']))
                    item = OrderedDict(values)
        return item
 
 
 
    def _fc_properties_of(self, cls):
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
    
        
    def _fc_describe(self, Base):
        result = []
        for name, cls in Base._decl_class_registry.items():
            if name in ['Audit']: continue
            try:
                if name[0] != "_":
                    pk, properties = self._fc_properties_of(cls)
                    result.append(OrderedDict([
                                   ("name", name),
                                   ("pk", pk),
                                   ("properties", properties)
                                   ]))
            except:
                logging(name)
                raise
        result.sort(key=lambda v: v['name'])
        return result
        
        