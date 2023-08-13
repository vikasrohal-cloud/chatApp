from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
import datetime
from flask_pymongo import PyMongo
import bcrypt
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/AIE_Chat_app"
mongo = PyMongo(app)

users = mongo.db.users
# db = client['AIE_Chat_App']


def fetch_chat_history(user_id, mobile_number):
    chat_history = []

    # Replace 'history' with your actual collection name
    collection = db['history']

    # Replace 'user_id' and 'mobile_no' with your field names
    query = {
        'user_id': user_id,
        'mobile_no': mobile_number
    }

    # Fetch chat history documents that match the query
    cursor = collection.find(query)

    for document in cursor:
        chat_history.append({
            'sender': document['sender'],
            'message': document['message'],
            'timestamp': document['timestamp']
        })

    return chat_history


@app.route("/")
def index():
    return render_template("index.html")

# @app.route("/login")
# def index():
#     return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = users.find_one({"username": request.form["username"]})
        user_contact = users.find_one({"contact no.": request.form["contact_number"]})
        if existing_user and user_contact is None:
            hashed_password = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt())
            users.insert_one({
                "username": request.form["username"],
                "password": hashed_password
            })
            session["username"] = request.form["username"]
            return redirect(url_for("dashboard"))
        # return "Username already exists!"
        return render_template("register.html", error_message="Username already exists!")

    return render_template("register.html")

def valid_mobile_number(mobile_number):
    # Remove spaces and hyphens from the mobile number
    mobile_number = mobile_number.replace(" ", "").replace("-", "")

    # Check if the mobile number consists of exactly 10 digits and is numeric
    if len(mobile_number) == 10 and mobile_number.isdigit():
        return True 
    else:
        return False


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile_number = request.form.get('mobile_number')
        password = request.form.get('password')
        # Validate mobile number and authenticate user
        if valid_mobile_number(mobile_number):
            session['user'] = mobile_number
            return redirect(url_for('/after_login.html'))
        else:
            error_message = "Invalid mobile number."
            return render_template("login.html", error_message=error_message)

    return render_template("login.html")


@app.route("/afterlogin")
def afterLogin():
        return render_template("after_login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# @app.route('/get_chat_history', methods=['GET'])
# def get_chat_history():
#     if 'user' in session:
#         # Retrieve chat history from MongoDB and return as JSON
#         return chat_history
#     return "Unauthorized", 401

if __name__ == '__main__':
    app.run(debug=True)
