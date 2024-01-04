from application import app, db
from application.models import User, insights, hypothesis
from functools import wraps
from flask import Flask, redirect, session, jsonify, request
from flask_cors import CORS,cross_origin
from datetime import datetime, timedelta

def login_required(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        session_id = request.json.get('session_id')
        query = {'session_id': session_id, 'expiry_date' : {'$gt' : datetime.utcnow()}}
        if db['logged_in'].find_one(query) is not None and session_id is not None:
            return f(*args, **kwargs)
        else:
            return jsonify ({"error": 'User is not logged in'}), 400
    return wrap

@app.route("/")
def home():
    return "home"


@app.route("/login", methods=['POST'])
def login():
    
    document = {
        'session_id' : request.json.get('session_id'),
        'expiry_date' : datetime.utcnow() + timedelta(hours=4)
    }
    db['logged_in'].insert_one(document)
    return "home"


@app.route("/signup", methods=['POST'])
@cross_origin()
def signup():
    return User().signup()

@app.route("/delete_session", methods=['POST'])
@cross_origin()
@login_required
def delete_session():
    session_id = request.json.get('session_id'),
    query = {'session_id' : session_id }
    if query is not None and session_id is not None:
        db['logged_in'].delete_many(query)
        
        return 'Session was deleted', 200
    else:
        return 'session never existed', 400
    
    


@app.route("/get_column_names")
@cross_origin()
@login_required
def get_column_names():
    names = list(db.cars.find_one().keys())
    # column_names = [ name.capitalize() for name in  names if name != '_id' ]
    column_names = [ name for name in  names if name != '_id' ]
    
    return jsonify({'column_names' :  column_names})


@app.route("/get_data", methods=['POST'])
@cross_origin()
@login_required
def get_data():
    column_name = request.json.get('column_name')
    if 'Fuel consumption inside cities (l/100km)'.lower() in column_name.lower():
        data = list(db.cars.find({'Fuel consumption inside cities (l/100km)': {'$gt': 0}}, {'_id': 0, 'model year': 1, 'Fuel consumption inside cities (l/100km)': 1}))
        return jsonify({'data' : data})

    if 'Electrical consumption inside cities (kwh/100km)'.lower() in column_name.lower():
        data = list(db.cars.find({'Electrical consumption inside cities (kwh/100km)': {'$gt': 0}}, {'_id': 0, 'model year': 1, 'Electrical consumption inside cities (kwh/100km)': 1}))
        return jsonify({'data' : data})
    else:
        return jsonify ({'data' : []})


@app.route("/get_insights", methods=['POST'])
@cross_origin()
@login_required
def get_insights():
    return insights().get_insights()


@app.route("/get_hypothesis", methods=['POST'])
@cross_origin()
@login_required
def get_hypothesis():
    return hypothesis().get_hypothesis()

# # Testing that the database was connected 
# @app.route("/<name>")
# def name(name):
       
#     users_collection = db['users']

#     # Insert the user data into the 'users' collection
#     users_collection.insert_one({'name': name, 'password': '123', 'DOB' : '1969-06-09'})
    

#     return f'User {name} added to the database.'
