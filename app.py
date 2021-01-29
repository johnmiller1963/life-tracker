""" Main file for the Life Tracker system, incorporating
    routing, logic and MongoDB interaction
"""

import os
from dateutil.parser import parse
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
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if user_email already exists in db
        existing_user = mongo.db.tbl_users.find_one(
            {"user_email": request.form.get("user_email").lower()})

        if existing_user:
            flash('User email already registered, please \
                use a different email!')

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
        flash("Welcome, {}".format(
            request.form.get("user_display_name")))
        return redirect(url_for("items", username=session["user_email"]))
    return render_template("register.html")


@app.route("/logon", methods=["GET", "POST"])
def logon():
    if request.method == "POST":
        # check if user email exists in mongo
        existing_user = mongo.db.tbl_users.find_one(
            {"user_email": request.form.get("user_email").lower()})

        if existing_user:
            # check hashed password matches user input
            if check_password_hash(
                existing_user["user_password_hash"], request.form.get(
                    "user_password")):
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


@app.route("/demo")
def demo():
    session.clear()
    session["user_email"] = "demo@life-tracker.co.uk"
    flash("Now viewing our Demo account")
    return redirect(url_for("items", username=session["user_email"]))


@app.route("/logout")
def logout():
    session.clear()
    flash("User logged out successfully")
    return redirect(url_for("home"))


@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "POST":
        if request.form.get("new_item_expiry_date"):
            optional_expiry_date = parse(request.form.get(
                "new_item_expiry_date"))
        else:
            optional_expiry_date = ""

        # This switch is important as it places items in the correct tab
        if request.form.get("new_item_recurs_months"):
            optional_recurs = (request.form.get("new_item_recurs_months"))
        else:
            optional_recurs = "0"

        one_new_item = {
            "item_user_email": session["user_email"].lower(),
            "item_title": request.form.get("new_item_title"),
            "item_description": request.form.get("new_item_description"),
            "item_cost": request.form.get("new_item_cost"),
            "item_start_date": datetime.now(),
            "item_expiry_date": optional_expiry_date,
            "item_hide": "off",
            "item_recurs_months": str(optional_recurs)
        }
        mongo.db.tbl_items.insert_one(one_new_item)
        flash("New item added successfully!")
        return redirect(url_for("items", username=session["user_email"]))

    items_renewables = list(
        mongo.db.tbl_items.find(
            {
                "item_user_email": session["user_email"],
                "item_hide": "off",
                "item_recurs_months": {"$gt": "0"},
            }
        ).sort([("item_expiry_date", 1)])
    )
    items_warranties = list(
        mongo.db.tbl_items.find(
            {
                "item_user_email": session["user_email"],
                "item_hide": "off",
                "item_recurs_months": "0",
            }
        ).sort([("item_expiry_date", 1)])
    )
    return render_template(
        "items.html",
        items_renewables=items_renewables,
        items_warranties=items_warranties,
    )


# Defined as a delete function, we are actually only 'hiding' the record
@app.route("/delete_item/<item_id>")
def delete_item(item_id):
    if session["user_email"] == "demo@life-tracker.co.uk":
        flash("The demo account cannot delete items!")
    else:
        myquery = {"_id": ObjectId(item_id)}
        newvalues = {"$set": {"item_hide": "on"}}

        mongo.db.tbl_items.update_one(myquery, newvalues)

        flash("Item deleted successfully!")
    return redirect(url_for("items", username=session["user_email"]))


@app.route("/edit_item/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if request.method == "POST":
        # This would be stopped by local JS, this just to be sure
        if session["user_email"] == "demo@life-tracker.co.uk":
            flash("The demo account cannot edit items!")
        else:
            if request.form.get("item_expiry_date" + item_id):
                optional_expiry_date = parse(request.form.get(
                    "item_expiry_date" + item_id))
            else:
                optional_expiry_date = ""

            if request.form.get("item_recurs_months" + item_id):
                optional_recurs = (request.form.get(
                    "item_recurs_months" + item_id))
            else:
                optional_recurs = "0"

            this_item = request.form.get("item_title" + item_id)

            edited_item = {"_id": ObjectId(item_id)}

            edited_values = {"$set": {
                "item_title": request.form.get("item_title" + item_id),
                "item_description": request.form.get(
                    "item_description" + item_id),
                "item_cost": request.form.get("item_cost" + item_id),
                "item_start_date": parse(request.form.get(
                    "item_start_date" + item_id)),
                "item_expiry_date": optional_expiry_date,
                "item_hide": "off",
                "item_recurs_months": str(optional_recurs)}
            }

            mongo.db.tbl_items.update_one(edited_item, edited_values)

            flash(this_item + ", updated successfully!")
        return redirect(url_for("items", username=session["user_email"]))
    return redirect(url_for("items", username=session["user_email"]))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
