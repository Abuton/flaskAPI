from model.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
engine = create_engine(
    "mysql://root@localhost:3306/bankAPI"
)
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))
bcrypt = Bcrypt(app)


def create_employees_accounts():
    name = "abu"
    username = "niceguy"
    usert = "employee"
    passw = "123"
    passw_hash = bcrypt.generate_password_hash(passw).decode("utf-8")
    db.execute(
        f"INSERT INTO employees (name, username, user_type, password) VALUES (:n,:u,:t,:p)",
        {"n": name, "u": username, "t": usert, "p": passw_hash},
    )
    db.commit()
    print("accounts Completed ............................................ ")

    name = "maria"
    username = "francisca"
    usert = "cashier"
    passw = "123"
    passw_hash = bcrypt.generate_password_hash(passw).decode("utf-8")
    db.execute(
        "INSERT INTO employees (name, username, user_type, password) VALUES (:n,:u,:t,:p)",
        {"n": name, "u":username, "t": usert, "p": passw_hash},
    )
    db.commit()
    print("accounts Completed ............................................ ")


def create_customers_accounts():
    cust_ssn_id = 1234
    name = "Arisha Barron"
    status = "Active"
    db.execute(
        "INSERT INTO customers (cust_ssn_id, name, status) VALUES (:c, :n, :s)",
        {"c": cust_ssn_id, "n": name, "s": status},
    )
    print(f"Customer with cust_ssn_id: {cust_ssn_id} has been created")

    cust_ssn_id = 4321
    name = "Branden Gibson"
    status = "Active"
    db.execute(
        "INSERT INTO customers (cust_ssn_id, name, status) VALUES (:c, :n, :s)",
        {"c": cust_ssn_id, "n": name, "s": status},
    )
    print(f"Customer with cust_ssn_id: {cust_ssn_id} has been created")


if __name__ == "__main__":
    try:
        # pre-populate db with some data
        create_customers_accounts()
        create_employees_accounts()
    except Exception as e:
        print("Error:", e)
