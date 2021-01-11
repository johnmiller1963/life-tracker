import os
from datetime import datetime
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def show_home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if user_email already exists in db
        existing_user = mongo.db.tbl_users.find_one(
            {"user_email": request.form.get("user_email").lower()})

        if existing_user:
            flash("User email already registered, please use a different email!")
            print("User email already registered, please use a different email!")
            return redirect(url_for("register"))

        register = {
            "user_email": request.form.get("user_email").lower(),
            "user_display_name": request.form.get("user_display_name").lower(),
            "user_authorised": True,
            "user_date_joined": datetime.now(),
            "user_demo_account": False,
            "password": generate_password_hash(
                request.form.get("user_password"),
                method='pbkdf2:sha256:80000')
        }
        mongo.db.tbl_users.insert_one(register)

        # put the new user into 'session' cookie
        session["user_email"] = request.form.get("user_email").lower()
        flash("User Registration Successful!")
        print("User Registration Successful!")

        # after correct registration direct user to add new items page NOT profile
        # return redirect(url_for("profile", username=session["user"]))
        return redirect(url_for("items", username=session["user_email"]))
    return render_template("register.html")


@app.route("/logon", methods=["GET", "POST"])
def logon():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("logon"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("logon"))

    return render_template("logon.html")


@app.route("/items")
def items():
    items = mongo.db.tbl_items.find()
    return render_template("items.html", items=items)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
