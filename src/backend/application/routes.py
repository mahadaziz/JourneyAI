from application import app, db
from application.models import User, insights
from functools import wraps
from flask import Flask, redirect, session, jsonify
from flask_cors import CORS,cross_origin

def login_required(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

@app.route("/")
def home():
    return "home"



@app.route("/signup", methods=['POST'])
@cross_origin()
def signup():
    return User().signup()

@app.route("/signout")
@login_required
@cross_origin()
def signout():
    return User().signout()

@app.route("/login", methods=['POST'])
@cross_origin()
def login():
    return User().login()


@app.route("/get_column_names")
@cross_origin()
@login_required
def get_column_names():
    names = list(db.cars.find_one().keys())
    column_names = [ name.capitalize() for name in  names if name != '_id' ]
    return jsonify({'column_names' :  column_names})




@app.route("/get_insights", methods=['POST'])
@cross_origin()
@login_required
def get_insights():
    return insights().get_insights()

# # Testing that the database was connected 
# @app.route("/<name>")
# def name(name):
       
#     users_collection = db['users']

#     # Insert the user data into the 'users' collection
#     users_collection.insert_one({'name': name, 'password': '123', 'DOB' : '1969-06-09'})
    

#     return f'User {name} added to the database.'
