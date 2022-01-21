import os
from flask import request, jsonify, Blueprint

from bankAPI.model.database import Base, Accounts, Transactions, CustomerLog, Customers
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from bankAPI.utils import random_with_N_digits
from flasgger import swag_from


bank = Blueprint("bank", __name__, url_prefix="/")
bank.secret_key = os.urandom(24)

# Set up database
engine = create_engine(
    "sqlite:///database.db", connect_args={"check_same_thread": False}, echo=True
)
# create db engine connection and start session
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))


# route to add customers
@bank.route("/addcustomer", methods=["POST"])
def addcustomer():
    """Add New Customers to the customers table in the db"""
    if request.method == "POST":
        cust_ssn_id = int(request.form.get("cust_ssn_id"))
        name = request.form.get("name")
        # ensure customer with same cust_ssn_id does not exist in the db
        customer = db.execute(
            "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
        ).fetchone()
        # check if customer_ssn_id is not in db
        if customer is not None:
            query = Customers(cust_ssn_id=cust_ssn_id, name=name, status="activate")
            # insert new customer
            db.add(query)
            db.commit()
            if query.cust_ssn_id is None:
                return jsonify(
                    success=False,
                    status_code=403,
                    message="Data is not inserted! Check you input",
                )
            else:
                temp = CustomerLog(
                    cust_ssn_id=query.cust_ssn_id, log_message="Customer Created"
                )
                # log the transaction into the customerlog table
                db.add(temp)
                db.commit()
                return jsonify(
                    success=True,
                    status_code=200,
                    message=f"Customer {query.name} is created with customer ID : {query.cust_ssn_id}.",
                )
        else:
            return jsonify(
                success=False,
                status_code=403,
                message=f"SSN id : {cust_ssn_id} is already present in database.",
            )


# route to edit customer
@bank.route("/editcustomer")
@bank.route("/editcustomer", methods=["GET", "POST"])
def editcustomer(cust_ssn_id=None):
    cust_ssn_id = int(request.form.get("cust_ssn_id"))
    if cust_ssn_id is not None:
        if request.method != "POST":
            cust_ssn_id = int(cust_ssn_id)
            data = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
            ).fetchone()
            if data is not None and data.status != "deactivate":
                return jsonify(success=True, status_code=200, message=dict(data))
            else:
                return jsonify(
                    success=False, status_code=404, message="Customer Info not found"
                )
        else:
            cust_ssn_id = int(cust_ssn_id)
            name = request.form.get("name")
            customer_info = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :c and status = 'activate'",
                {"c": cust_ssn_id},
            ).fetchone()
            if customer_info is not None:
                customer_info = db.execute(
                    "UPDATE customers SET name = :n WHERE cust_ssn_id = :a",
                    {"n": name, "a": cust_ssn_id},
                )
                db.commit()
                temp = CustomerLog(
                    cust_ssn_id=cust_ssn_id, log_message="Customer Data Updated"
                )
                db.add(temp)
                db.commit()
                return jsonify(
                    success=False,
                    status_code=200,
                    message="Customer data are updated successfully",
                )
            else:
                return jsonify(
                    success=False,
                    status_code=403,
                    message="Invalid customer Id. Please, check customer Id.",
                )


# route to deactivate customers account
@bank.route("/deletecustomer")
@bank.route("/deletecustomer")
def deletecustomer():
    cust_ssn_id = int(request.form.get("cust_ssn_id"))

    if cust_ssn_id is not None:
        cust_ssn_id = int(cust_ssn_id)
        customer_info = db.execute(
            "SELECT * from customers WHERE cust_ssn_id = :a and status = 'activate'",
            {"a": cust_ssn_id},
        ).fetchone()
        if customer_info is not None:
            query = db.execute(
                "UPDATE customers SET status='deactivate' WHERE cust_ssn_id = :a",
                {"a": cust_ssn_id},
            )
            db.commit()
            temp = CustomerLog(
                cust_ssn_id=cust_ssn_id, log_message="Customer Deactivated"
            )
            db.add(temp)
            db.commit()
            return jsonify(
                success=False,
                status_code=403,
                message="Customer is Successfully deactivated.",
            )
        else:
            return jsonify(
                success=False,
                status_code=403,
                message=f"Customer with id : {cust_ssn_id} is already deactivated or not present in database.",
            )
    else:
        return jsonify(
            sucess=False, status_code=403, message="Customer ID can't be None"
        )


@bank.route("/addaccount", methods=["POST"])
@swag_from("./docs/bankfunctions/addaccount.yaml")
def addaccount():
    """Route to add new account for customers"""
    if request.method == "POST":
        # get data from form
        cust_ssn_id = int(request.form.get("cust_ssn_id"))
        acc_type = request.form.get("acc_type")
        amount = float(request.form.get("amount"))
        message = "Account successfully created"

        # allow initial deposit of amount not less than 100
        if amount < 100:
            return jsonify(
                success=False,
                status_code=403,
                message="Amount should not be less than $100",
            )
        # get customer that wants to add a new account
        customer_info = db.execute(
            "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
        ).fetchone()
        if customer_info is not None:
            # get random 10 digits number as account_id
            account_id = random_with_N_digits(10)
            query = Accounts(
                acc_id=account_id,
                acc_type=acc_type,
                balance=amount,
                cust_ssn_id=cust_ssn_id,
                status="active",
                message=message,
            )
            # add the new account to accounts table
            db.add(query)
            db.commit()
            if query.acc_id is None:
                jsonify(
                    success=False,
                    status_code=403,
                    message="Data is not inserted! Check you input.",
                )
            else:
                return jsonify(
                    success=True,
                    status_code=200,
                    message=f"{query.acc_type} account is created with customer ID : {query.cust_ssn_id}.",
                )
        else:
            return jsonify(
                success=False,
                status_code=403,
                message=f"Customer with id: {cust_ssn_id} is not present in database.",
            )


# Adding route to transfer amount
@bank.route("/transfer", methods=["POST"])
@swag_from("./docs/bankfunctions/transfer.yaml")
def transfer():
    """Route to allow transfer of amount between accounts"""
    cust_ssn_id = int(request.form.get("cust_ssn_id"))
    if cust_ssn_id is None:
        return jsonify(
            success=False, status_code=404, message="Customer ID can't be None"
        )
    else:
        if request.method == "POST":
            # get data from form
            src_acc_id = request.form.get("src_acc_id")
            trg_acc_id = request.form.get("trg_acc_id")
            amount = int(request.form.get("amount"))
            # check if the two accounts are different
            if src_acc_id != trg_acc_id:
                # get source data i.e where the amount will be transferred
                src_data = db.execute(
                    "select * from accounts where acc_id = :a and status='active'",
                    {"a": src_acc_id},
                ).fetchone()
                # get target data i.e where the amount will be deposited
                trg_data = db.execute(
                    "select * from accounts where cust_ssn_id = :a and status='active'",
                    {"a": trg_acc_id},
                ).fetchone()
                if src_data is not None and trg_data is not None:
                    # check if amount is not greater than the src amount
                    if src_data.balance > amount:
                        try:
                            # then perform the transaction
                            src_balance = src_data.balance - amount
                            trg_balance = trg_data.balance + amount
                            # update the src account
                            src_update = db.execute(
                                "update accounts set balance = :b where acc_id = :a",
                                {"b": src_balance, "a": src_acc_id},
                            )
                            db.add(src_update)
                            db.commit()
                            temp = Transactions(
                                acc_id=src_data.acc_id,
                                trans_message="Amount Transfered to "
                                + str(trg_data.acc_id),
                                amount=amount,
                                transaction_type="TRANSFER",
                            )
                            # log the transaction
                            db.add(temp)
                            db.commit()
                            # update the target account
                            trg_update = db.execute(
                                "update accounts set balance = :b where acc_id = :a",
                                {"b": trg_balance, "a": trg_acc_id},
                            )
                            # log the transaction
                            db.add(trg_update)
                            db.commit()
                            src_update = Transactions(
                                acc_id=trg_data.acc_id,
                                trans_message="Amount received from "
                                + str(src_data.acc_id),
                                amount=amount,
                                transaction_type="DEPOSIT",
                            )
                            db.add(src_update)
                            db.commit()

                            return jsonify(
                                message=f"Amount transfered to {trg_data.acc_id} from {src_data.acc_id} successfully",
                                success=True,
                                status_code=200,
                            )
                        except Exception as e:
                            raise e

                    else:
                        return jsonify(
                            success=False,
                            status_code=403,
                            message=f"{src_data.acc_id} has insufficient balance",
                        )

                elif src_data and not trg_data:
                    transfer_account_error = jsonify(
                        success=False,
                        status_code=404,
                        message=f"Target account {trg_data.acc_id} not Found",
                    )
                    return transfer_account_error

                elif trg_data and not src_data:
                    return jsonify(
                        success=False,
                        status_code=404,
                        message=f"Source account {src_data.acc_id} not Found",
                    )
                else:
                    return jsonify(
                        success=False,
                        status_code=404,
                        message="Both accounts not Found try different ones",
                    )
            else:
                return jsonify(
                    success=False,
                    status_code=403,
                    message="Can't transfer to the same account",
                )


# route to retrievebalance
@bank.route("/retrievebalance", methods=["GET"])
@swag_from("./docs/bankfunctions/retrivebalance.yaml")
def retrieve_balance():
    """Route to retrieve account balance for a given account"""

    account_number = request.args.get("account_number")

    if request.method == "GET":
        # check if account_number provided is valid/exist in db
        account = db.execute(
            "select * from accounts where acc_id = :a", {"a": account_number}
        ).fetchone()
        if account is None:
            balance_account_error = jsonify(
                success=False,
                status_code=404,
                message="Account not Found. Try a different one",
            )
            return balance_account_error
        else:
            # get balance from accounts based on acc_id
            balance = db.execute(
                "select balance from accounts where acc_id = :a", {"a": account_number}
            ).fetchone()
            if balance is not None:
                return jsonify(
                    success=True,
                    status_code=200,
                    message=f"Account balance is {balance['amount']}",
                )


# route to retrieve transfer history
@bank.route("/transferhistory", methods=["GET"])
@swag_from("./docs/bankfunctions/retrivetransferhistory.yaml")
def retrieve_transfer_history():
    """Route to retrieve transfer history"""
    account_number = request.args.get("account_number")

    if request.method == "GET":
        account = db.execute(
            "select * from transactions where acc_id = :a", {"a": account_number}
        ).fetchall()
        # check if user exists in db
        if account is not None and len(account) >= 1:
            # get transfer history
            transfer_history = db.execute(
                "select * from transactions where acc_id = :a and transaction_type = 'TRANSFER' ",
                {"a": account_number},
            )
            if transfer_history is not None:
                transfer_history = jsonify(
                    success=True,
                    status_code=200,
                    history=[a._asdict() for a in account_transfer_his],
                )
                return transfer_history
        else:
            transfer_history_error = jsonify(
                success=False,
                status_code=404,
                message="Account not Found.try different one",
            )
            return transfer_history_error
