from application import app, db
from application.models import User, insights, hypothesis
from functools import wraps
from flask import Flask, redirect, session, jsonify, request
from flask_cors import CORS,cross_origin
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename

############################
# def login_required(f):
#     @wraps(f)
#     def wrap (*args, **kwargs):
#         try:
#             session_id = request.json.get('session_id')
#         except:
#             session_id = request.form['session_id']
            
#         query = {'session_id': session_id}
#         if db['logged_in'].find_one(query) is not None and session_id is not None:
#             return f(*args, **kwargs)
#         else:
#             return jsonify ({"error": 'User is not logged in'}), 400
#     return wrap
###############################

# Home Route, doesn't do much
@app.route("/")
def home():
    return "home"


############# Login is happening in the frontend using json tokens (NEXTAUTH) ##################
# @app.route("/login", methods=['POST'])
# def login():
    
#     document = {
#         'session_id' : request.json.get('session_id')
#         }
#     db['logged_in'].insert_one(document)
#     return "home"
################################################################################################

# Route for signing in 
@app.route("/signup", methods=['POST'])
@cross_origin()
def signup():
    return User().signup()

#############  Backend session are no longer used ##################
# @app.route("/delete_session", methods=['POST'])
# @cross_origin()
# #@login_required
# def delete_session():
#     session_id = request.json.get('session_id'),
#     query = {'session_id' : session_id }
#     if query is not None and session_id is not None:
#         db['logged_in'].delete_many(query)
        
#         return 'Session was deleted', 200
#     else:
#         return 'session never existed', 400
#####################################################################    
  
  
 # Get list of topics   
@app.route("/get_topics", methods=['POST'])
@cross_origin()
#@login_required
def get_topics():
    user_id = request.json.get('user_id')
    title = request.json.get('title')
    query = {'title' : title, 'user_id' : user_id }
    if db['datasets'].find_one(query):
        try:
            if db['datasets'].find_one(query)['column_names']:
                doc = db['datasets'].find_one(query)['column_names']
                return jsonify ({'title' : doc['title'],'column_names' : doc['column_names']}), 200
        except:
            return jsonify({'message' : 'column_names not populated in database for specified dataset'}), 400
    else:
        return jsonify({'message' : f'The dataset with {title} does not exist for user {user_id}'}), 400
    


# Get the column names for the cars dataset
@app.route("/get_column_names", methods=['POST'])
@cross_origin()
#@login_required
def get_column_names():
    names = list(db.cars.find_one().keys())
    # column_names = [ name.capitalize() for name in  names if name != '_id' ]
    column_names = [ name for name in  names if name != '_id' ]
    
    return jsonify({'column_names' :  column_names})


# Get some data from the graphs dataset
@app.route("/get_data", methods=['POST'])
@cross_origin()
#@login_required
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


# Route to call the get_insights functions in the insights class in models.py
@app.route("/get_insights", methods=['POST'])
@cross_origin()
#@login_required
def get_insights():
    return insights().get_insights()


# Route to call the get_hypothesis function in the hypothesis class in models.py
@app.route("/get_hypothesis", methods=['POST'])
@cross_origin()
#@login_required
def get_hypothesis():
    return hypothesis().get_hypothesis()

### Testing that the database was connected ############
# @app.route("/<name>")
# def name(name):
       
#     users_collection = db['users']

#     # Insert the user data into the 'users' collection
#     users_collection.insert_one({'name': name, 'password': '123', 'DOB' : '1969-06-09'})
    

#     return f'User {name} added to the database.'
###########################################################   

# Route to upload dataset  
@app.route("/upload_dataset", methods = ['POST'])
@cross_origin()
#@login_required
def input_dataset():
    file = request.files['file']
    df = None
    if file:
        file.filename = secure_filename(file.filename)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file).to_dict(orient='records')
            names = list(df[0].keys())
            column_names = [ name for name in  names if name != '_id' ]
            db['datasets'].insert_one({'title': request.form['title'], 'user_id': request.form['user_id'], 'data': df, 'created_date': datetime.utcnow(),
            'last_update_time': datetime.utcnow(), 'column_names' : column_names  })
        
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file).to_dict(orient='records')
            names = list(df[0].keys())
            column_names = [ name for name in  names if name != '_id' ]
            db['datasets'].insert_one({'title': request.form['title'], 'user_id': request.form['user_id'], 'data': df, 'created_date': datetime.utcnow(),
            'last_update_time': datetime.utcnow(), 'column_names' : column_names  })
        
        elif file.filename.endswith('.json'):
            df = pd.read_json(file).to_dict(orient='records')
            names = list(df[0].keys())
            column_names = [ name for name in  names if name != '_id' ]
            db['datasets'].insert_one({'title':request.form['title'], 'user_id': request.form['user_id'], 'data': df, 'created_date': datetime.utcnow(),
            'last_update_time': datetime.utcnow(), 'column_names' : column_names })
             
        else:
            return jsonify({"message" : 'Unsupported file format'}), 400
        
        
        document = {
            'user_id': request.form['user_id'],
            'title' : request.form['title'],
            'text' : '',
            'text_description' : '',
            'current-hypothesis' : [],
            'current_insights' : [],
            'graph_state' : [],
            'favorites' : {'insights' : [], 'hypothesis' : [], 'graphs' : []}
}
        db['documents'].insert_one(document)
        
        try:
            names = list(df[0].keys())
            column_names = [ name for name in  names if name != '_id' ]
            return jsonify({'column_names' :  column_names, 'title' : request.form['title']}), 200
        except:
            return jsonify({'message' :  'Could not get a list of column_names'}), 400
    else:
        return jsonify({'message' :  'The file is undefined'}), 400
    
    # TODO :: Generate All Insights


########## Route for one time indexing of mongodb database ############
# @app.route("/index_table")
# def index_table():
#     db['datasets'].create_index([('user_id', 1), ('title', 1)])
#######################################################################
