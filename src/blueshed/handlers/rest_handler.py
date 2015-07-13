'''
Created on 12 Feb 2014

@author: peterb
'''
import logging
from blueshed.utils.utils import loads, dumps
from blueshed.handlers.base_handler import BaseHandler
from collections import OrderedDict


class RestHandler(BaseHandler):
    """
        Simple rest hanlder with  no authentication
        that expects the fecth_and_carry mixin to be
        mixed into the control
    """
    
     
    def prepare(self):
        if self.request.headers.get("Content-Type") == "application/json" and \
            self.request.body:
            self.json_args = loads(str(self.request.body,encoding="UTF-8"))
        else:
            self.json_args = None
            
            
    def require_json_content(self):
        if self.request.headers.get("Content-Type") != "application/json":
            raise Exception("Content-Type 'application/json' required")
    
    
    def get(self, resource_path):
        """
            Get goes to fetch_and_carry_mixin fetch or returns the meta data
        """
        logging.info("get %s",resource_path)
        if resource_path is None or resource_path is "":
            self.write(OrderedDict([
                ("target", "rest-api"),
                ("version", 1),
                ("post_methods", self.control._fc_methods),
                ("model", self.control._fc_description)
            ]))
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
        """
            Post calls public methods on the control
        """
        self.require_json_content()
        logging.info("post %s - %s",resource_path, self.json_args)
        resources = resource_path.split("/")
        action = resources[0]
        try:
            logging.debug(resource_path)
            args = self.json_args or {}
            
            method = getattr(self.control, action)
                
            result = method(self.current_user, **args)
            self.write(dumps({"result": result},indent=2))
            self.control._flush()
            
        except Exception as ex:
            logging.exception(ex)
            error = str(ex)
            self.write(dumps({"result": None,
                              "error" : error },indent=2))
            self.control._flush(ex)
            
        
    def put(self,resource_path):
        """
            Put goes to fetch_and_carry_mixin carry
        """
        self.require_json_content()
        logging.info("put %s - %s",resource_path, self.json_args)
        try:
            resources = resource_path.split("/")
            resource = resources[0]
            id = int(resources[1]) if len(resources) > 1 else None
            args = self.json_args
            item = args.get("item")
            if item is None:
                raise Exception("json payload: {item:obj, (to_add:[attr,type,id]]), (to_remove:[attr,type,id]])}")
            if item.get("_type") is None and resource in [None,""]:
                raise Exception("No resource specified")
            if item.get("_type") is None:
                item["_type"] = resource
            result = {"result": self.control.carry(self.get_current_user,
                                                   item,
                                                   args.get("to_add"),
                                                   args.get("to_remove")), "action": "saved" }
        except Exception as ex:
            result = {"error": str(ex)}
            self.control._flush(ex)
            logging.exception(ex)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(dumps(result))
        self.control._flush()
        
        
    def delete(self, resource_path):
        """
            Put goes to fetch_and_carry_mixin carry
        """
        self.require_json_content()
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
        
    