import unittest
import requests
import json
from pprint import pprint
from base import BaseTestCase


class BackAPITest(BaseTestCase):
    # Ensure that retrievebalance route works as expected
    # def test_retrievebalance(self):
    #     response = requests.get(self.URL+"/retrievebalance")
    #     data = response.json()

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('message', data.keys())
    #     # self.assertGreater(data['balance'] > 0)

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
        self.assertEqual(response["status_code"], 200)
        self.assertIn("created", response["message"])

    def test_transfer_amount_success(self):
        params = {
            "cust_ssn_id": "1234",
            "src_acc_id": "222906",
            "trg_acc_id": "781303",
            "amount": "2"
            }

        response = requests.post(self.URL + "/transfer", data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        self.assertEqual(response["status_code"], 200)
        self.assertIn("successfully", response["message"])

    def test_transfer_same_account_error(self):
        params = {"cust_ssn_id": "1234",
                  "src_acc_id": "222906",
                  "trg_acc_id": "222906",
                  "amount": "150"}

        response = requests.post(self.URL + "/transfer", data=params)
        response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response["status_code"], 403)
        self.assertIn("Can't transfer to", response["message"])

    def test_transfer_customer_id_error(self):
        params = {
            "cust_ssn_id": "32131",
            "src_acc_id": "222906",
            "trg_acc_id": "781303",
            "amount": 200
        }
        response = requests.post(self.URL + "/transfer", data=params)
        response = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response["status_code"], 404)
        self.assertIn("Customer ID can't be None", response["message"])

    def test_transfer_amount_error(self):
        params = {
            "cust_ssn_id": "1234",
            "src_acc_id": "222906",
            "trg_acc_id": "781303",
            "amount": 1000
            }

        response = requests.post(self.URL + "/transfer", data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        self.assertEqual(response["status_code"], 403)
        self.assertIn("insufficient balance", response["message"])

    def test_transfer_trg_id_error(self):
        params = {
            "cust_ssn_id": "1234",
            "src_acc_id": "222906",
            "trg_acc_id": "211122",
            "amount": 100
            }

        response = requests.post(self.URL + "/transfer", data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        self.assertEqual(response["status_code"], 404)
        self.assertIn("Target account not found", response["message"])

    def test_transfer_src_id_error(self):
        params = {
            "cust_ssn_id": "1234",
            "src_acc_id": "209906",
            "trg_acc_id": "781303",
            "amount": "300"
            }

        response = requests.post(self.URL + "/transfer", data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        self.assertEqual(response["status_code"], 404)
        self.assertIn("Source account not found", response["message"])

    def test_retrieve_transfer_history_success(self):
        params = {"account_number": "222906"}

        response = requests.post(self.URL + '/transferhistory', data=params)
        response = response.content.decode("utf-8")
        response = json.loads(response)
        # print("TR History", response)
        self.assertEqual(response["status_code"], 200)
        self.assertIn("TRANSFER", response["history"])

    def test_retrieve_transfer_history_error(self):
        params = {"account_number": "123456"}

        response = requests.post(self.URL + '/transferhistory', data=params)
        response = response.content.decode("utf-8")
        print("TR Error History", response)
        response = json.loads(response)
        print("TR Error History", response)
        self.assertEqual(response["status_code"], 403)
        self.assertIn("Account not Found", response["message"])


if __name__ == "__main__":
    unittest.main()
