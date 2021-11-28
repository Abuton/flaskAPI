# import dependencies
import os
import functools
from flask import (
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
    Blueprint
)
# from flask_bcrypt import Bcrypt
from bankAPI.model.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# documentation
from flasgger import swag_from

auth = Blueprint("auth", __name__, url_prefix="/")
# bcrypt = Bcrypt(auth)
auth.secret_key = os.urandom(24)

# Set up database
engine = create_engine(
    "sqlite:///database.db", connect_args={"check_same_thread": False}, echo=True
)
# create db engine connection and start session
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))


# route for 404 error
@auth.errorhandler(404)
def not_found(e):
    return render_template("404.html")


# route for 500 error
@auth.errorhandler(500)
def unexpected_condition(e):
    return render_template("500.html")


def login_required(view):
    """View decorator that redirects anonymous users to the login page"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view


# LOGIN
@auth.route("/login")
@swag_from("./docs/auth/login.yaml")
def login():
    """Log in registered employee by adding the username to the session."""
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password").encode("utf-8")
        user = db.execute(
            "SELECT * FROM employees WHERE username = :u", {"u": usern}
        ).fetchone()
        if user is not None:
            # if bcrypt.check_password_hash(user["password"], passw) is True:
            if user["password"] == passw:
                session["username"] = user.username
                session["namet"] = user.name
                session["usert"] = user.user_type
                flash(
                    f"{user.name.capitalize()}, you are successfully logged in!",
                    "success",
                )
                return redirect(url_for("dashboard"))
            else:
                flash("Incorrect Username or Password.", "danger")
        flash("Sorry, Username or password does not match.", "danger")
    return render_template("login.html")


# Logout
@auth.route("/logout")
@swag_from("./docs/auth/logout.yaml")
def logout():
    """Clear the current session, including the stored username"""
    session.clear()
    return redirect(url_for("login"))
