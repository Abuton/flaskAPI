import unittest
import requests
import json
from pprint import pprint
from base import BaseTestCase


class BackAPITest(BaseTestCase):
    # Ensure that retrievebalance route works as expected
    def test_retrievebalance(self):
        response = requests.get(self.URL+"/retrievebalance")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data.keys())
        # self.assertGreater(data['balance'] > 0)

    # Ensure transferhistory route works as expected
    def test_transferhistory(self):
        response = requests.get(self.URL+f"/transferhistory")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(data), 0)

    # Ensure addaccount route works as expected
    def test_addaccount_less_than_default(self):
        params = {
            "cust_ssn_id": "4321",
            "acc_type": "test",
            "amount": "56"
        }

        response = requests.post(self.URL + '/addaccount', data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        self.assertEqual(response["status_code"], 403)
        self.assertEqual(response["success"], False)
        self.assertIn("$100", response["message"])

    def test_addaccount_success(self):
        params = {
            "cust_ssn_id": "1234",
            "acc_type": "test",
            "amount": "560"
        }

        response = requests.post(self.URL + '/addaccount', data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        pprint(response)
        self.assertEqual(response["status_code"], 200)
        self.assertIn("created", response["message"])


if __name__ == "__main__":
    unittest.main()
