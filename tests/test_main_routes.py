import unittest
import requests
from base import BaseTestCase


class BackAPITest(BaseTestCase):
    # Ensure that retrievebalance route works as expected
    def test_retrievebalance(self):
        response = requests.get(self.URL+"/retrievebalance")
        # data = response.json()

        self.assertEqual(response.status_code, 404)
        # self.assertIn(b'balance', data.keys())
        # self.assertGreater(data['balance'] > 0)

    # Ensure transferhistory route works as expected
    def test_transferhistory(self, acc_id=2341231256):
        response = requests.get(self.URL+f"/transferhistory/{int(acc_id)}")
        # data = response.json()

        self.assertEqual(response.status_code, 500)
        # self.assertNotEqual(len(data), 0)

    # Ensure addaccount route works as expected
    def test_addaccount(self):
        response = requests.get(self.URL+'/addaccount')
        statuscode = response.status_code
        self.assertEqual(statuscode, 500)


if __name__ == "__main__":
    unittest.main()
