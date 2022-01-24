import datetime
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import mysql.connector as mysql

Base = declarative_base()


def DBConnect(dbName=None):
    conn = mysql.connect(host='localhost', user='root',
                         database=dbName, buffered=True)
    cur = conn.cursor()
    return conn, cur


def createDB(dbName: str) -> None:
    conn, cur = DBConnect()
    cur.execute(f"DROP DATABASE IF EXISTS {dbName};")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {dbName} CHARSET = utf8mb4 DEFAULT COLLATE = utf8mb4_unicode_ci;")
    conn.commit()
    cur.close()


# model for employees table
class Employees(Base):
    """
    Employee Model to store employee information
    """

    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    user_type = Column(String(20), nullable=False)
    password = Column(String(250))

    def __init__(self, name, username, user_type, password):
        self.name = name
        self.username = username
        self.user_type = user_type
        self.password = password

    def __repr__(self):
        return '<username - {}>'.format(self.username)


# model for customers table
class Customers(Base):
    """
    Customer Model to store customer information
    """

    __tablename__ = "customers"
    cust_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_ssn_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    status = Column(String(10), nullable=False)
    # initialize the relationship from the Customers table with accounts & Customerlog table
    acc_id = relationship("Accounts", backref="acc_cust_ssn_id", lazy=True)
    customer_log = relationship("CustomerLog", backref="cust_ssn_id_log", lazy=True)

    def __init__(self, cust_ssn_id, name, status):
        self.cust_ssn_id = cust_ssn_id
        self.name = name
        self.status = status

    def __repr__(self):
        return '<cust_ssn_id - {}>'.format(self.cust_ssn_id)


# model for customer's log table
class CustomerLog(Base):
    """
    CustomerLog Model: to store customer activities
    """

    __tablename__ = "customerlog"
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_ssn_id = Column(Integer, ForeignKey("customers.cust_ssn_id"))
    log_message = Column(String(250), nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.datetime.now())

    def __init__(self, cust_ssn_id, log_message):
        self.cust_ssn_id = cust_ssn_id
        self.log_message = log_message

    def __repr__(self):
        return '<message - {}>'.format(self.log_message)


# model for account table
class Accounts(Base):
    """
    Account Model to store account information for customers
    the model has a one to many relationship with customers and
    another with the Transaction model
    """

    __tablename__ = "accounts"
    acc_id = Column(Integer, primary_key=True)
    acc_type = Column(String(20), nullable=False)
    balance = Column(Integer, nullable=False)
    cust_ssn_id = Column(Integer, ForeignKey("customers.cust_ssn_id"), nullable=False)
    status = Column(String(10), nullable=False)
    message = Column(String(250))
    last_update = Column(DateTime(timezone=False), default=datetime.datetime.now())
    # initialize the relationship from the Customers table with accounts & Customerlog table
    trans_id = relationship("Transactions", backref="trans_acc_id", lazy=True)

    def __init__(self, acc_id, acc_type, balance, cust_ssn_id, status, message):
        self.acc_id = acc_id
        self.acc_type = acc_type
        self.balance = balance
        self.cust_ssn_id = cust_ssn_id
        self.status = status
        self.message = message

    def __repr__(self):
        return '<cust_ssn_id - {} and message - {}>'.format(self.cust_ssn_id, self.log_message)


# model for transaction table
class Transactions(Base):
    """
    Transaction Model to store all transactions
    """

    __tablename__ = "transactions"
    trans_id = Column(Integer, primary_key=True, autoincrement=True)
    acc_id = Column(Integer, ForeignKey("accounts.acc_id"), nullable=False)
    trans_message = Column(String(250), nullable=False)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.datetime.now())

    def __init__(self, acc_id, trans_message, amount, transaction_type):
        self.acc_id = acc_id
        self.trans_message = trans_message
        self.amount = amount
        self.transaction_type = transaction_type

    def __repr__(self):
        return '<trans_message - {}>'.format(self.trans_message)


if __name__ == "__main__":
    try:
        # create the database
        createDB(dbName='bankAPI')
        engine = create_engine("mysql://root@localhost:3306/bankAPI", echo=False)
        Base.metadata.create_all(engine)
        print("All Model Created Successfully!")
    except Exception as e:
        print("Error", e)
