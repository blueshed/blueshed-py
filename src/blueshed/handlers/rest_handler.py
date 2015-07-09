'''
Created on 12 Feb 2014

@author: peterb
'''
import logging
from blueshed.utils.utils import loads, dumps
from blueshed.handlers.base_handler import BaseHandler


class RestHandler(BaseHandler):
    """
        Simple rest hanlder with  no authentication
        that expects the fecth_and_carry mixin to be
        mixed into the control
    """
    
     
    def prepare(self):
        if self.request.headers.get("Content-Type") == "application/json":
            self.json_args = loads(str(self.request.body,encoding="UTF-8")) 
    
    
    def get(self, resource_path):
        logging.info("get %s",resource_path)
        if resource_path is None or resource_path is "":
            self.write({
                "target": "rest-api",
                "version": 1,
                "model":self.control.describe(self.current_user)
            })
        else:
            try:
                resources = resource_path.split("/")
                resource = resources[0]
                id = resources[1] if len(resources) > 1 else None
                limit = int(self.get_argument("limit", 10))
                offset = int(self.get_argument("offset", 0))
                attr = self.get_argument("attr", None)
                filter = self.get_argument("filter", None)
                match = self.get_argument("match", None)
                order_by = self.get_argument("order_by", None)
                order_by_asc = self.get_argument("order_by_asc", 'false').lower() == "true"
                depth = int(self.get_argument("depth", 0))
                ignore = self.get_argument("ignore",None)
                include = self.get_argument("include",None)
                if ignore:
                    ignore = ignore.split(",")
                if include:
                    include = include.split(",")
                result = {"result": self.control.fetch(1,resource,id, 
                                                       attr=attr,
                                                       filter=filter,
                                                       match=match,
                                                       limit=limit, 
                                                       offset=offset,
                                                       order_by=order_by,
                                                       order_by_asc=order_by_asc,
                                                       depth=depth,
                                                       ignore=ignore,
                                                       include=include)}
            except Exception as ex:
                result = {"error": str(ex)}
                logging.exception(ex)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(dumps(result))
        
    
    def post(self,resource_path):
        self._save(resource_path)
        
    def put(self,resource_path):
        self._save(resource_path)
    
    def _save(self, resource_path):
        logging.info("put %s - %s",resource_path, self.json_args)
        try:
            resources = resource_path.split("/")
            resource = resources[0]
            id = int(resources[1]) if len(resources) > 1 else None
            item = self.json_args
            item["_type"] = resource
            item["id"] = id
            result = {"result": self.control.carry(1,item), "action": "saved" }
        except Exception as ex:
            result = {"error": str(ex)}
            logging.exception(ex)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(dumps(result))
        
        
    def delete(self, resource_path):
        logging.info("delete %s",resource_path)
        try:
            resources = resource_path.split("/")
            resource = resources[0]
            id = int(resources[1])
            result = {"result": self.control.carry(1,{"id":-id,"_type":resource}) , "action": "deleted"}
        except Exception as ex:
            result = {"error": str(ex)}
            logging.exception(ex)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(dumps(result))
        
    