'''
Created on 11 Jul 2015

@author: peterb
'''
import unittest
from faker.factory import Factory
from tornado.testing import AsyncTestCase
from tornado.httpclient import AsyncHTTPClient
from blueshed.utils.utils import loads, dumps

BASE_URL = "http://localhost:8080/rest/"

class Test(AsyncTestCase):
    
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch(BASE_URL, self._handle_fetch,
                     headers={"simple-auth-token":"--foo-bar--"})
        self.wait()

    def _handle_fetch(self, response):
        result = loads(response.body.decode("utf-8"))
        self.assertDictContainsSubset({"version": 1}, result, "should have been there")
        self.assertEquals(len(result["model"]),4)
        self.stop()
        
    
    def test_http_put(self):
        fake = Factory.create("en_GB")
        client = AsyncHTTPClient(self.io_loop)
        for _ in range(10):
            data = {"item":{
                "email":     fake.email(),
                "firstname": fake.first_name(),
                "lastname":  fake.last_name(),
                "_password": fake.password()
            }}
            client.fetch("{}Person".format(BASE_URL), self.stop, 
                         method="PUT", 
                         body=dumps(data),
                         headers={"Content-Type": "application/json",
                                  "simple-auth-token":"--foo-bar--"})
            response = self.wait()
            result = loads(response.body.decode("utf-8"))
            if result.get("error"):
                raise Exception(result["error"])
            
        for _ in range(10):
            data = {"item":{
                "name":  fake.name(),
                "dob": fake.date(),
                "active": fake.pybool(),
                "customer_type": "retail"
            }}
            client.fetch("{}Customer".format(BASE_URL), self.stop, 
                         method="PUT", 
                         body=dumps(data),
                         headers={"Content-Type": "application/json",
                                  "simple-auth-token":"--foo-bar--"})
            response = self.wait()
            result = loads(response.body.decode("utf-8"))
            if result.get("error"):
                raise Exception(result["error"])
            
            data = {
                "item": {
                    "line1":  fake.address(),
                    "town": fake.city(),
                    "postcode": fake.postcode(),
                    "customer_type": "retail"
                },
                "to_add": [
                           [
                            "customers",
                            "Customer",
                            result["result"]["id"]
                           ]
                        ]
            }
            client.fetch("{}Address".format(BASE_URL), self.stop, 
                         method="PUT", 
                         body=dumps(data),
                         headers={"Content-Type": "application/json",
                                  "simple-auth-token":"--foo-bar--"})
            response = self.wait()
            result = loads(response.body.decode("utf-8"))
            
        



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()