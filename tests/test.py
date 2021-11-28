import unittest
from flask import request
from base import BaseTestCase
from bankAPI import create_app


class BankAPITestBasic(BaseTestCase):
    """ """
    # Ensure that main page requires user login
    def test_main_route_requires_login(self):
        self.app = create_app()
        self.client = self.app.test_client()
        response = request.get('/', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    # Ensure that dashboard page loads
    def test_welcome_route_works_as_expected(self):
        response = request.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Welcome to our bank!', response.data)

    # Ensure that flask app is set up correctly
    def test_index(self):
        response = request.get(self.URL+'/')
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
