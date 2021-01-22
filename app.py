import os
from locale import currency
from datetime import datetime
from dateutil.parser import parse
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
            "user_display_name": request.form.get("user_display_name"),
            "user_authorised": True,
            "user_date_joined": datetime.now(),
            "user_demo_account": False,
            "user_password_hash": generate_password_hash(
                request.form.get("user_password"))
        }
        mongo.db.tbl_users.insert_one(register)

        # put the new user into 'session' cookie
        session["user_email"] = request.form.get("user_email").lower()
        flash("User Registration Successful!")
        flash("Welcome, {}".format(
            request.form.get("user_display_name")))
        #print("User Registration Successful!")

        # after correct registration direct user to add new items page NOT profile
        # return redirect(url_for("profile", username=session["user"]))
        return redirect(url_for("items", username=session["user_email"]))
    return render_template("register.html")


@app.route("/logon", methods=["GET", "POST"])
def logon():
    if request.method == "POST":
        # check if user email exists in db
        existing_user = mongo.db.tbl_users.find_one(
            {"user_email": request.form.get("user_email").lower()})
        #print("The next value is the existing_user variable for email...")
        #print(request.form.get("user_email").lower())
        #print(existing_user["user_email"])
        #print(existing_user["user_display_name"])
        #print(existing_user["user_password_hash"])
        #flash({{existing_email["user_display_name"]}})
        if existing_user:
            # check hashed password matches user input
            #flash("Found existing user")
            if check_password_hash(existing_user["user_password_hash"], request.form.get("user_password")):
                session["user_email"] = request.form.get("user_email").lower()
                flash("Welcome back, {}".format(
                    existing_user["user_display_name"]))
                return redirect(url_for(
                    "items", username=session["user_email"]))
            else:
                # invalid password match
                flash("Incorrect Email and/or Password")
                return redirect(url_for("logon"))

        else:
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            return redirect(url_for("logon"))

    return render_template("logon.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("User logged out successfully")
    return redirect(url_for("show_home"))


@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "POST":
        one_new_item = {
            "item_user_email": session["user_email"].lower(),
            "item_title": request.form.get("new_item_title"),
            "item_description": request.form.get("new_item_description"),
            "item_cost": request.form.get("new_item_cost"),
            "item_start_date": datetime.now(),
            "item_expiry_date": parse(request.form.get("new_item_expiry_date")),
            "item_hide": "off",
            "item_recurs_months": request.form.get("new_item_recurs_months")
        }
        mongo.db.tbl_items.insert_one(one_new_item)
        flash("New item added successfully!")
        return redirect(url_for("items", username=session["user_email"]))

    items = list(mongo.db.tbl_items.find({"item_user_email": session["user_email"], "item_hide": "off"}).sort([("item_expiry_date", 1)]))
    return render_template("items.html", items=items)


@app.route("/delete_item", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        delete_item = {"item_hide": "on"},
        {"$set": {"_id": "5fe9b44435640f187ac1ff35"}}

        mongo.db.tbl_items.update_one(delete_item)
        flash("Item deleted successfully!")
        return redirect(url_for("items", username=session["user_email"]))

    items = list(mongo.db.tbl_items.find({"item_user_email": session["user_email"], "item_hide": "off"}).sort([("item_expiry_date", 1)]))
    return render_template("items.html", items=items)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
