import sys
import os
import unittest
from bankAppServer import app


class FlaskTestCase(unittest.TestCase):
    """docstring for FlaskTestCase
    A class for unit-testing some of the function/method in the
    app.py file
    Args:
        unittest.TestCase this allows the new class to inherit
        from the unittest module
    """

    # check status code for the home page at route (/demo1)
    def test_homepage(self):
        tester = app.test_client(self)
        response = tester.get('/')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)


if __name__ == "__main__":
    unittest.main()
