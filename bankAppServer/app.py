import os
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify, Response
from marshmallow.fields import Method
from flask_bcrypt import Bcrypt
from flask_session import Session
from model.database import Base,Accounts,Customers,Users,CustomerLog,Transactions
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)

# Set up database
engine = create_engine('sqlite:///database.db',connect_args={'check_same_thread': False},echo=True)
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))


app = Flask(__name__)


# homepage
@app.route('/')
def homepage():
    return "Banking API"


@app.route("/addcustomer", methods=["GET", "POST"])
def addcustomer():
    if 'user' not in session:
        # redirect to login page
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if request.method == "POST":
            cust_ssn_id = int(request.form.get("cust_ssn_id"))
            name = request.form.get("name")
            result = db.execute("SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}).fetchone()
            if result is None :
                result = db.query(Customers).count()
                if result == 0 :
                    query = Customers(cust_id=110110000,cust_ssn_id=cust_ssn_id,name=name, status='activate')
                else:
                    query = Customers(cust_ssn_id=cust_ssn_id,name=name, status='activate')
                db.add(query)
                db.commit()
                if query.cust_id is None:
                    flash("Data is not inserted! Check you input.","danger")
                else:
                    temp = CustomerLog(cust_id=query.cust_id,log_message="Customer Created")
                    db.add(temp)
                    db.commit()
                    flash(f"Customer {query.name} is created with customer ID : {query.cust_id}.","success")
                    return redirect(url_for('viewcustomer'))
            flash(f'SSN id : {cust_ssn_id} is already present in database.','warning')
        
    # return render_template('addcustomer.html', addcustomer=True)
    return "Add Customers Page"


@app.route("/viewcustomer/<cust_id>")
@app.route("/viewcustomer" , methods=["GET", "POST"])
def viewcustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if request.method == "POST":
            cust_ssn_id = request.form.get("cust_ssn_id")
            cust_id = request.form.get("cust_id")
            data = db.execute("SELECT * from customers WHERE cust_id = :c or cust_ssn_id = :d", {"c": cust_id, "d": cust_ssn_id}).fetchone()
            if data is not None:
                return render_template('viewcustomer.html', viewcustomer=True, data=data)
            
            flash("Customer not found! Please,Check you input.", 'danger')
        elif cust_id is not None:
            data = db.execute("SELECT * from customers WHERE cust_id = :c", {"c": cust_id}).fetchone()
            if data is not None:
                return render_template('viewcustomer.html', viewcustomer=True, data=data)
            
            flash("Customer not found! Please,Check you input.", 'danger')
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))

    return render_template('viewcustomer.html', viewcustomer=True)


@app.route('/editcustomer')
@app.route('/editcustomer/<cust_id>', methods=["GET", "POST"])
def editcustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if cust_id is not None:
            if request.method != "POST":
                cust_id = int(cust_id)
                data = db.execute("SELECT * from customers WHERE cust_id = :c", {"c": cust_id}).fetchone()
                if data is not None and data.status != 'deactivate':
                    return render_template('editcustomer.html', editcustomer=True, data=data)
                else:
                    flash('Customer is deactivated or not present in database.','warning')
            else:
                cust_id = int(cust_id)
                name = request.form.get("name")
                result = db.execute("SELECT * from customers WHERE cust_id = :c and status = 'activate'", {"c": cust_id}).fetchone()
                if result is not None :
                    result = db.execute("UPDATE customers SET name = :n WHERE cust_id = :a", {"n": name, "a": cust_id})
                    db.commit()
                    temp = CustomerLog(cust_id=cust_id,log_message="Customer Data Updated")
                    db.add(temp)
                    db.commit()
                    flash(f"Customer data are updated successfully.","success")
                else:
                    flash('Invalid customer Id. Please, check customer Id.','warning')

    return redirect(url_for('viewcustomer'))


@app.route('/deletecustomer')
@app.route('/deletecustomer/<cust_id>')
def deletecustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if cust_id is not None:
            cust_id = int(cust_id)
            result = db.execute("SELECT * from customers WHERE cust_id = :a and status = 'activate'", {"a": cust_id}).fetchone()
            if result is not None :
                query = db.execute("UPDATE customers SET status='deactivate' WHERE cust_id = :a", {"a": cust_id})
                db.commit()
                temp = CustomerLog(cust_id=cust_id,log_message="Customer Deactivated")
                db.add(temp)
                db.commit()
                flash(f"Customer is deactivated.","success")
                return redirect(url_for('dashboard'))
            else:
                flash(f'Customer with id : {cust_id} is already deactivated or not present in database.','warning')
    return redirect(url_for('viewcustomer'))


@app.route('/activatecustomer')
@app.route('/activatecustomer/<cust_id>')
def activatecustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if cust_id is not None:
            cust_id = int(cust_id)
            result = db.execute("SELECT * from customers WHERE cust_id = :a and status = 'deactivate'", {"a": cust_id}).fetchone()
            if result is not None :
                query = db.execute("UPDATE customers SET status='activate' WHERE cust_id = :a", {"a": cust_id})
                db.commit()
                temp = CustomerLog(cust_id=cust_id,log_message="Customer Activated")
                db.add(temp)
                db.commit()
                flash(f"Customer is activated.","success")
                return redirect(url_for('dashboard'))
            flash(f'Customer with id : {cust_id} is already activated or not present in database.','warning')
    return redirect(url_for('viewcustomer'))


@app.route('/activateaccount')
@app.route('/activateaccount/<acc_id>')
def activateaccount(acc_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if acc_id is not None:
            acc_id = int(acc_id)
            result = db.execute("SELECT * from accounts WHERE acc_id = :a and status = 'deactive'", {"a": acc_id}).fetchone()
            if result is not None :
                date = datetime.datetime.now()
                query = db.execute("UPDATE accounts SET status='active', message='Account Activated Again', last_update = :d WHERE acc_id = :a", {"d":date,"a": acc_id})
                db.commit()
                flash(f"Account is activated.","success")
                return redirect(url_for('dashboard'))
            flash(f'Account with id : {acc_id} is already activated or not present in database.','warning')
    return redirect(url_for('viewaccount'))


@app.route("/addaccount" , methods=["GET", "POST"])
def addaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if request.method == "POST":
            cust_id = int(request.form.get("cust_id"))
            acc_type = request.form.get("acc_type")
            amount= float(request.form.get("amount"))
            message = "Account successfully created"
            if amount < 100:
                flash("Amount should be greater or equal to 100")
            result = db.execute("SELECT * from customers WHERE cust_id = :c", {"c": cust_id}).fetchone()
            if result is not None:
                result = db.execute("SELECT * from accounts WHERE cust_id = :c and acc_type = :at", {"c": cust_id, "at": acc_type}).fetchone()
                if result is None:
                    result = db.query(Accounts).count()
                    if result == 0:
                        query = Accounts(acc_id=360110000,acc_type=acc_type,balance=amount,cust_id=cust_id,status='active',message=message,last_update=datetime.datetime.now())
                    else:
                        query = Accounts(acc_type=acc_type,balance=amount,cust_id=cust_id,status='active',message=message,last_update=datetime.datetime.now())
                    db.add(query)
                    db.commit()
                    if query.acc_id is None:
                        flash("Data is not inserted! Check you input.","danger")
                    else:
                        flash(f"{query.acc_type} account is created with customer ID : {query.acc_id}.","success")
                        return redirect(url_for('dashboard'))
                else:
                    flash(f'Customer with id : {cust_id} has already {acc_type} account.','warning')
            else:
                flash(f'Customer with id : {cust_id} is not present in database.','warning')

    return render_template('addaccount.html', addaccount=True)


@app.route("/delaccount" , methods=["GET", "POST"])
def delaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="employee":
        if request.method == "POST":
            acc_id = int(request.form.get("acc_id"))
            result = db.execute("SELECT * from accounts WHERE acc_id = :a and status='active'", {"a": acc_id}).fetchone()
            if result is not None :
                # delete from accounts WHERE acc_id = :a and acc_type=:at", {"a": acc_id,"at":acc_type}
                message = "Account Deactivated"
                date = datetime.datetime.now()
                query = db.execute("UPDATE accounts SET status='deactive', message= :m, last_update = :d WHERE acc_id = :a;", {"m":message,"d":date,"a": acc_id})
                db.commit()
                flash(f"Customer account is Deactivated Successfully.","success")
                return redirect(url_for('dashboard'))
            flash(f'Account with id : {acc_id} is already deactivate or account not found.','warning')
    return render_template('delaccount.html', delaccount=True)


@app.route("/retrievebalance")
@app.route("/retrievebalance/<acc_id>", methods=['GET', "POST"])
def retrieve_balance(acc_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == 'employee':
        if acc_id is None:
            flash("Enter a valid account number")
            return redirect(url_for('retrievebalance'))
        query = db.execute(f"select acc_id from accounts where acc_id = {acc_id}")
        if query is None:
            flash("Account ID does not exist")
        if request.method == "GET":
            balance = db.execute(f"select balance from accounts where acc_id = {acc_id}".fetchone())
            flash(f"Remaining Balance for account id {acc_id} is {balance}")
            return render_template('retrievebalace.html')


@app.route('/transferhistory/<acc_id>')
def retrieve_transfer_history(acc_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == 'employee':
        if acc_id is None:
            flash("Enter a valid account number")
            return redirect(url_for('transferhistory'))
        query = db.execute(f"select acc_id from accounts where acc_id = {acc_id}")
        if query is None:
            flash("Account ID does not exist")
        if request.method == "GET":
            transfer_history = db.execute(f"select * from transactions where acc_id = {acc_id} and transaction_type = 'TRANSFER' ".fetchall())
            flash(f"Transfer History for account id {acc_id} is {transfer_history}")
            return render_template('transferhistory.html')


@app.route('/transfer',methods=['GET','POST'])
@app.route('/transfer/<cust_id>',methods=['GET','POST'])
def transfer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "employee":
        if cust_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == 'POST':
                src_type = request.form.get("src_type")
                trg_type = request.form.get("trg_type")
                amount = int(request.form.get("amount"))
                if src_type != trg_type:
                    src_data  = db.execute("select * from accounts where cust_id = :a and acc_type = :t and status='active'",{"a":cust_id,"t":src_type}).fetchone()
                    trg_data  = db.execute("select * from accounts where cust_id = :a and acc_type = :t and status='active'",{"a":cust_id,"t":trg_type}).fetchone()
                    if src_data is not None and trg_data is not None:
                        if src_data.balance > amount:
                            src_balance = src_data.balance - amount
                            trg_balance = trg_data.balance + amount
                            
                            test = db.execute(f"update accounts set balance = {src_balance} where cust_id = {cust_id} and acc_type = {src_type}")
                            db.commit()
                            temp = Transactions(acc_id=src_data.acc_id,trans_message="Amount Transfered to "+str(trg_data.acc_id),amount=amount, transaction_type="TRANSFER")
                            db.add(temp)
                            db.commit()

                            db.execute(f"update accounts set balance = {trg_balance} where cust_id = {cust_id} and acc_type = {trg_type}")
                            db.commit()
                            temp = Transactions(acc_id=trg_data.acc_id,trans_message="Amount received from "+str(src_data.acc_id),amount=amount, transaction_type="DEPOSIT")
                            db.add(temp)
                            db.commit()

                            flash(f"Amount transfered to {trg_data.acc_id} from {src_data.acc_id} successfully",'success')
                        else:
                            flash("Insufficient amount to transfer.","danger")
                            
                    else:
                        flash("Accounts not found","danger")

                else:
                    flash("Can't Transfer amount to same account.",'warning')

            else:
                data = db.execute("select * from accounts where cust_id = :a",{"a":cust_id}).fetchall()
                if data and len(data) == 2:
                    return render_template('transfer.html', deposit=True, cust_id=cust_id)
                else:
                    flash("Data Not found or Invalid Customer ID",'danger')
                    return redirect(url_for('viewaccount'))

    return redirect(url_for('dashboard'))


# route for 404 error
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


# route for 404 error
@app.errorhandler(500)
def not_found(e):
  return render_template("500.html") 


# Logout 
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        usern = request.form.get("username").upper()
        passw = request.form.get("password").encode('utf-8')
        result = db.execute("SELECT * FROM users WHERE id = :u", {"u": usern}).fetchone()
        if result is not None:
            if bcrypt.check_password_hash(result['password'], passw) is True:
                session['user'] = usern
                session['namet'] = result.name
                session['usert'] = result.user_type
                flash(f"{result.name.capitalize()}, you are successfully logged in!", "success")
                return redirect(url_for('dashboard'))
        flash("Sorry, Username or password not match.","danger")
    return render_template("login.html", login=True)


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
