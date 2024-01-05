from application import app, db
from application.models import User, insights, hypothesis
from functools import wraps
from flask import Flask, redirect, session, jsonify, request
from flask_cors import CORS,cross_origin
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename

def login_required(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        try:
            session_id = request.json.get('session_id')
        except:
            session_id = request.form['session_id']
            
        query = {'session_id': session_id}
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
        'session_id' : request.json.get('session_id')
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
    
    


@app.route("/get_column_names", methods=['POST'])
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

@app.route("/upload_dataset", methods = ['POST'])
@cross_origin()
@login_required
def input_dataset():
    file = request.files['dataset']
    df = None
    if file:
        file.filename = secure_filename(file.filename)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file).to_dict(orient='records')
            db['datasets'].insert_one({'title': request.form['title'], 'user_id': request.form['user_id'], 'data': df, 'created_date': datetime.datetime.utcnow(),
            'last_update_time': datetime.datetime.utcnow() })
        
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file).to_dict(orient='records')
            db['datasets'].insert_one({'title': request.form['title'], 'user_id': request.form['user_id'], 'data': df, 'created_date': datetime.datetime.utcnow(),
            'last_update_time': datetime.datetime.utcnow() })
        
        elif file.filename.endswith('.json'):
            df = pd.read_json(file).to_dict(orient='records')
            db['datasets'].insert_one({'title':request.form['title'], 'user_id': request.form['user_id'], 'data': df, 'created_date': datetime.datetime.utcnow(),
            'last_update_time': datetime.datetime.utcnow() })
        
        else:
            return jsonify({"message" : 'Unsupported file format'}), 400
        
        try:
            names = list(df.keys())
            column_names = [ name for name in  names if name != '_id' ]
            return jsonify({'column_names' :  column_names, 'title' : request.form['title']}), 200
        except:
            return jsonify({'message' :  'Could not get a list of column_names'}), 400
    else:
        return jsonify({'message' :  'The file is undefined'}), 400
    # Generate All Insights


@app.route("/index_table")
def index_table():
    db['datasets'].create_index([('user_id', 1), ('title', 1)])

