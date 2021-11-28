import os
from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Blueprint,
)

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
@bank.route("/addcustomer", methods=["GET", "POST"])
def addcustomer():
    """Add New Customers to the customers table in the db"""
    # check if user is logged in
    if "user" not in session:
        # redirect to login page
        return redirect(url_for("login"))
    # check if user_type is employee
    if session["usert"] == "employee":
        if request.method == "POST":
            cust_ssn_id = int(request.form.get("cust_ssn_id"))
            name = request.form.get("name")
            # ensure customer with same cust_ssn_id does not exist in the db
            customer = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
            ).fetchone()
            # check if customer_ssn_id is not in db
            if customer is None:
                query = Customers(cust_ssn_id=cust_ssn_id, name=name, status="activate")
                # insert new customer
                db.add(query)
                db.commit()
                if query.cust_ssn_id is None:
                    flash("Data is not inserted! Check you input.", "danger")
                else:
                    temp = CustomerLog(
                        cust_ssn_id=query.cust_ssn_id, log_message="Customer Created"
                    )
                    # log the transaction into the customerlog table
                    db.add(temp)
                    db.commit()
                    flash(
                        f"Customer {query.name} is created with customer ID : {query.cust_ssn_id}.",
                        "success",
                    )
                    return redirect(url_for("viewcustomer"))

            flash(f"SSN id : {cust_ssn_id} is already present in database.", "warning")
            redirect(url_for("addcustomer"))

    return render_template("addcustomer.html")


# route to view customers
@bank.route("/viewcustomer/<cust_ssn_id>")
@bank.route("/viewcustomer", methods=["GET", "POST"])
def viewcustomer(cust_ssn_id=None):
    # check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    if session["usert"] == "employee":
        if request.method == "POST":
            cust_ssn_id = request.form.get("cust_ssn_id")
            cust_ssn_id = request.form.get("cust_ssn_id")
            # get customer info from the customers table
            data = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :c or cust_ssn_id = :d",
                {"c": cust_ssn_id, "d": cust_ssn_id},
            ).fetchone()
            if data is not None:
                return render_template("viewcustomer.html", data=data)

            flash("Customer not found! Please,Check you input.", "danger")
        # get customer info based on the passed cust_ssn_id
        elif cust_ssn_id is not None:
            data = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
            ).fetchone()
            if data is not None:
                return render_template("viewcustomer.html", data=data)

            flash("Customer not found! Please,Check you input.", "danger")
    else:
        flash("You don't have access to this page", "warning")
        return redirect(url_for("dashboard"))

    return render_template("viewcustomer.html")


# route to edit customer
@bank.route("/editcustomer")
@bank.route("/editcustomer/<cust_ssn_id>", methods=["GET", "POST"])
def editcustomer(cust_ssn_id=None):
    if "user" not in session:
        return redirect(url_for("login"))
    if session["usert"] == "employee":
        if cust_ssn_id is not None:
            if request.method != "POST":
                cust_ssn_id = int(cust_ssn_id)
                data = db.execute(
                    "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
                ).fetchone()
                if data is not None and data.status != "deactivate":
                    return render_template(
                        "editcustomer.html", editcustomer=True, data=data
                    )
                else:
                    flash(
                        "Customer is deactivated or not present in database.", "warning"
                    )
            else:
                cust_ssn_id = int(cust_ssn_id)
                name = request.form.get("name")
                result = db.execute(
                    "SELECT * from customers WHERE cust_ssn_id = :c and status = 'activate'",
                    {"c": cust_ssn_id},
                ).fetchone()
                if result is not None:
                    result = db.execute(
                        "UPDATE customers SET name = :n WHERE cust_ssn_id = :a",
                        {"n": name, "a": cust_ssn_id},
                    )
                    db.commit()
                    temp = CustomerLog(
                        cust_ssn_id=cust_ssn_id, log_message="Customer Data Updated"
                    )
                    db.add(temp)
                    db.commit()
                    flash(f"Customer data are updated successfully.", "success")
                else:
                    flash("Invalid customer Id. Please, check customer Id.", "warning")

    return redirect(url_for("viewcustomer"))


# route to deactivate customers account
@bank.route("/deletecustomer")
@bank.route("/deletecustomer/<cust_ssn_id>")
def deletecustomer(cust_ssn_id=None):
    if "user" not in session:
        return redirect(url_for("login"))
    if session["usert"] == "employee":
        if cust_ssn_id is not None:
            cust_ssn_id = int(cust_ssn_id)
            result = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :a and status = 'activate'",
                {"a": cust_ssn_id},
            ).fetchone()
            if result is not None:
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
                flash(f"Customer is deactivated.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash(
                    f"Customer with id : {cust_ssn_id} is already deactivated or not present in database.",
                    "warning",
                )
    return redirect(url_for("viewcustomer"))


@bank.route("/addaccount", methods=["GET", "POST"])
@swag_from("./docs/bankfunctions/addaccount.yaml")
def addaccount():
    """Route to add new account for customers"""
    # check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    # ensure user logged in is of type employee
    if session["usert"] == "employee":
        if request.method == "POST":
            # get data from form
            cust_ssn_id = int(request.form.get("cust_ssn_id"))
            acc_type = request.form.get("acc_type")
            amount = float(request.form.get("amount"))
            message = "Account successfully created"

            # allow initial deposit of amount not less than 100
            if amount < 100:
                flash("Amount should be greater or equal to 100")
            # get customer that wants to add a new account
            result = db.execute(
                "SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}
            ).fetchone()
            if result is not None:
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
                    flash("Data is not inserted! Check you input.", "danger")
                else:
                    flash(
                        f"{query.acc_type} account is created with customer ID : {query.cust_ssn_id}.",
                        "success",
                    )
                    return redirect(url_for("dashboard"))
            else:
                flash(
                    f"Customer with id: {cust_ssn_id} is not present in database.",
                    "warning",
                )
                redirect(url_for("addcustomer"))

    return render_template("viewaccount.html")


# Adding route to transfer amount
@bank.route("/transfer", methods=["POST"])
@swag_from("./docs/bankfunctions/transfer.yaml")
def transfer(cust_ssn_id=None):
    """Route to allow transfer of amount between accounts"""
    # check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    if session["usert"] == "employee":
        if cust_ssn_id is None:
            return redirect(url_for("viewaccount"))
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

                            flash(
                                f"Amount transfered to {trg_data.acc_id} from {src_data.acc_id} successfully",
                                "success",
                            )
                        else:
                            flash("Insufficient amount to transfer.", "danger")

                    else:
                        flash("Accounts not found", "danger")

                else:
                    flash("Can't Transfer amount to same account.", "warning")

    return redirect(url_for("dashboard"))


# route to retrievebalance
@bank.route("/retrievebalance/<acc_id>", methods=["GET", "POST"])
@swag_from("./docs/bankfunctions/retrivebalance.yaml")
def retrieve_balance(acc_id):
    """Route to retrieve account balance for a given account"""
    # check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    if session["usert"] == "employee":
        if request.method == "GET":
            # check if acc_id provided is valid/exist in db
            account = db.execute(
                "select * from accounts where acc_id = :a", {"a": acc_id}
            ).fetchone()
            if account is None:
                flash("Data Not Present in the DataBase")
                return redirect(url_for("retrievebalance"))
            else:
                # get balance from accounts based on acc_id
                balance = db.execute(
                    "select balance from accounts where acc_id = :a", {"a": acc_id}
                ).fetchone()
                if balance is not None:
                    flash(f"Remaining Balance for account id {acc_id} is {balance}")
                    return render_template("retrievebalace.html", balance=balance)

    return redirect(url_for("dashboard"))


# route to retrieve transfer history
@bank.route("/transferhistory")
@bank.route("/transferhistory/<acc_id>")
@swag_from("./docs/bankfunctions/retrivetransferhistory.yaml")
def retrieve_transfer_history(acc_id):
    """Route to retrieve transfer history"""
    # check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    if session["usert"] == "employee":
        if request.method == "GET":
            account = db.execute(
                "select * from transactions where acc_id = :a", {"a": acc_id}
            ).fetchall()
            # check if user exists in db
            if account is not None:
                # get transfer history
                transfer_history = db.execute(
                    "select * from transactions where acc_id = :a and transaction_type = 'TRANSFER' ",
                    {"a": acc_id},
                )
                if transfer_history is not None:
                    flash(
                        f"Transfer History for account id {acc_id} = {transfer_history}"
                    )
                    transfer_history = jsonify(transfer_history)
                    return render_template(
                        "transferhistory.html", transfer_history=transfer_history
                    )
            else:
                flash("The Account Provided does not exist")
                return redirect(url_for("transferhistory"))

    return redirect(url_for("dashboard"))
