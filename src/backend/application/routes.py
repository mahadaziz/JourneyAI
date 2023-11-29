from application import app, db
from application.models import User, insights
from functools import wraps
from flask import Flask, redirect, session, jsonify
from flask_cors import CORS,cross_origin


@app.route("/")
def home():
    return "home"



@app.route("/signup", methods=['POST'])
@cross_origin()
def signup():
    return User().signup()




@app.route("/get_column_names")
@cross_origin()
def get_column_names():
    names = list(db.cars.find_one().keys())
    # column_names = [ name.capitalize() for name in  names if name != '_id' ]
    column_names = [ name for name in  names if name != '_id' ]
    
    return jsonify({'column_names' :  column_names})


@app.route("/get_data", methods=['POST'])
@cross_origin()
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
def get_insights():
    return insights().get_insights()

# # Testing that the database was connected 
# @app.route("/<name>")
# def name(name):
       
#     users_collection = db['users']

#     # Insert the user data into the 'users' collection
#     users_collection.insert_one({'name': name, 'password': '123', 'DOB' : '1969-06-09'})
    

#     return f'User {name} added to the database.'
