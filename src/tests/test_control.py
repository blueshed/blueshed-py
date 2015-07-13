'''
Created on 9 Jun 2015

@author: peterb
'''
import unittest
from faker.factory import Factory
from examples.simple.control import Control
from examples.simple import model_ext


class Test(unittest.TestCase):


    def setUp(self):
        self.control = Control("sqlite:///test.db",drop_all=True)


    def tearDown(self):
        pass
    
    
    def testDescribe(self):
        print(self.control.describe(1))


    def testPeople(self):
        fake = Factory.create("en_GB")
        with self.control.session as session:
            for _ in range(100):
                puser = session.query(model_ext.Permission).filter_by(name="user").first()
                p = model_ext.Person(email=fake.email(),
                                         firstname=fake.first_name(),
                                         lastname=fake.last_name(),
                                         _password=fake.password())
                session.add(p)
                p.permissions.append(puser)
            session.commit()
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()