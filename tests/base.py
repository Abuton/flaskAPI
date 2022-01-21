import unittest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join('..')))

from bankAPI.app import db
from bankAPI import create_app
from bankAPI.model.database import Employees, Customers, Base


class BaseTestCase(unittest.TestCase):
    """A base test case"""
    URL = "http://127.0.0.1:5000"

    def setUp(self):
        self.bank = create_app()
        # Set up database
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        # create db engine connection and start session
        Base.metadata.bind = engine
        db = scoped_session(sessionmaker(bind=engine))

        emp = Employees("john mary", "jonny", "employee", "8712")
        db.add(emp)
        db.commit()
        cust = Customers(5432, "Ibrahim Mubarak", "active")
        db.add(cust)
        db.commit()

    def test_login(self):
        # Given
        payload = json.dumps({
            "username": "jonny",
            "password": "8712"
        })

        # When
        response = requests.get(self.URL, headers={"Content-Type": "application/json"}, params=payload)

        self.assertEqual(str, type(response.text))
        self.assertEqual(200, response.status_code)

    def tearDown(self):
        db.remove()


if __name__ == "__main__":
    unittest.main()
