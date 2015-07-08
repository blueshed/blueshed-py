'''
Created on 12 Feb 2014

@author: peterb
'''
import logging
from blueshed.utils.utils import dumps, loads
from blueshed.handlers.base_handler import BaseHandler


class RestHandler(BaseHandler):
    
     
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
                result = {"result": self.control.fetch(1,resource,id, limit=limit, offset=offset)}
            except Exception as ex:
                result = {"error": str(ex)}
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
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(dumps(result))
        
    