from application import app, db
from application.models import User, insights, hypothesis
from pathlib import Path
from bson.errors import InvalidDocument
from pymongo.errors import DocumentTooLarge
from flask import Flask, redirect, session, jsonify, request
from flask_cors import CORS,cross_origin
from datetime import datetime, timedelta
import pandas as pd



# Home Route, doesn't do much
@app.route("/")
def home():
    return "home"


# Route for signing in 
@app.route("/signup", methods=['POST'])
@cross_origin()
def signup():
    return User().signup()


  
@app.route("/good_hypothesis", methods=['POST'])
@cross_origin()
def good_hypothesis():
    hypo_id = request.json.get('hypothesis_id')
    curr = db['Hypothesis_logs'].find_one({'_id': hypo_id})
    
    if not curr['Thumbs_Up']:
        
        modified = db['Hypothesis_logs'].update_one(
            {'_id': hypo_id},
            {'$set': {'Thumbs_Up': True, 'Thumbs_Down': False}}
        )
        if modified.modified_count:
            return jsonify({'message': 'Thumps Up Successful'}), 200
        else:
            return jsonify({'message': 'Thumps Up Failed'}), 404
    if curr['Thumbs_Up']:
        
        modified = db['Hypothesis_logs'].update_one(
            {'_id': hypo_id},
            {'$set': {'Thumbs_Up': False, 'Thumbs_Down': False}}
        )
        if modified.modified_count:
            return jsonify({'message': 'Undoing Thumps Up Successful'}), 200
        else:
            return jsonify({'message': 'Undoing Thumps Up Failed'}), 404


@app.route("/bad_hypothesis", methods=['POST'])
@cross_origin()
def bad_hypothesis():
    hypo_id = request.json.get('hypothesis_id')
    curr = db['Hypothesis_logs'].find_one({'_id': hypo_id})
    
    if not curr['Thumbs_Down']:
        
        modified = db['Hypothesis_logs'].update_one(
            {'_id': hypo_id},
            {'$set': {'Thumbs_Up': False, 'Thumbs_Down': True}}
        )
        if modified.modified_count:
            return jsonify({'message': 'Thumps Down Successful'}), 200
        else:
            return jsonify({'message': 'Thumps Down Failed'}), 404
    if curr['Thumbs_Down']:
        
        modified = db['Hypothesis_logs'].update_one(
            {'_id': hypo_id},
            {'$set': {'Thumbs_Up': False, 'Thumbs_Down': False}}
        )
        if modified.modified_count:
            return jsonify({'message': 'Undoing Thumps Down Successful'}), 200
        else:
            return jsonify({'message': 'Undoing Thumps Down Failed'}), 404

# Get list of topics   
@app.route("/get_topics", methods=['POST'])
@cross_origin()
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
def get_column_names():
    row = db.cars.find_one({}, {'_id': 0}) or {}
    return jsonify({'column_names': list(row)})


# Get some data from the graphs dataset
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


# Route to call the get_insights functions in the insights class in models.py
@app.route("/get_insights", methods=['POST'])
@cross_origin()
def get_insights():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Expected a JSON object.'), 400
    column = payload.get('column_name')
    count = payload.get('insight_count', 18)
    previous = payload.get('prev_insights', [])
    if not isinstance(column, str) or type(count) is not int or count < 1:
        return jsonify(error='Choose a column and a positive insight count.'), 400
    if not isinstance(previous, list) or not all(isinstance(item, str) for item in previous):
        return jsonify(error='Invalid insight history.'), 400
    if 'rows' in payload:
        rows = payload['rows']
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            return jsonify(error='Expected an array of dataset rows.'), 400
    else:
        rows = db.cars.find({}, {'_id': 0})
    return insights(rows).generate_insights(column, previous, count)


# Route to call the get_hypothesis function in the hypothesis class in models.py
@app.route("/get_hypothesis", methods=['POST'])
@cross_origin()
def get_hypothesis():
    return hypothesis().get_hypothesis()


@app.route("/upload_dataset", methods=['POST'])
@cross_origin()
def input_dataset():
    file = request.files.get('file')
    title = request.form.get('title', '').strip()
    if not file or not title:
        return jsonify(error='Choose a file and enter a title.'), 400
    ticket = db.upload_tickets.find_one_and_delete({
        '_id': request.form.get('upload_ticket'), 'expires_at': {'$gt': datetime.utcnow()},
    })
    if not ticket:
        return jsonify(error='Sign in and retry the upload.'), 401
    user_id = ticket['user_id']

    readers = {'.csv': pd.read_csv, '.json': pd.read_json, '.xlsx': pd.read_excel}
    reader = readers.get(Path(file.filename).suffix.lower())
    if not reader:
        return jsonify(error='Unsupported file format.'), 400
    try:
        frame = reader(file)
    except (ValueError, UnicodeError):
        return jsonify(error='The file could not be read as a dataset.'), 400
    frame.columns = frame.columns.map(str)
    frame = frame.drop(columns=['_id'], errors='ignore')
    if frame.empty:
        return jsonify(error='Include a header and at least one data row.'), 400

    now = datetime.utcnow()
    columns = list(frame.columns)
    rows = frame.astype(object).where(frame.notna(), None).to_dict('records')
    try:
        result = db.datasets.insert_one({
            'user_id': user_id, 'title': title, 'column_names': columns, 'data': rows,
            'created_date': now, 'last_update_time': now,
        })
    except DocumentTooLarge:
        return jsonify(error='This dataset is too large to store. Try a smaller file.'), 413
    except InvalidDocument:
        return jsonify(error='The dataset contains unsupported field names or values.'), 400

    dataset_id = str(result.inserted_id)
    try:
        db.documents.insert_one({
            'user_id': user_id, 'dataset_id': dataset_id, 'title': title,
            'text': '', 'text_description': '', 'current-hypothesis': [],
            'current_insights': [], 'graph_state': [],
            'favorites': {'insights': [], 'hypothesis': [], 'graphs': []},
        })
    except Exception:
        db.datasets.delete_one({'_id': result.inserted_id})
        raise

    return jsonify(dataset_id=dataset_id, title=title, column_names=columns)
