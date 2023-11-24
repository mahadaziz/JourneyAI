from flask import Flask, jsonify, request, session, redirect
from application import db
import bcrypt, datetime, uuid

class User:
    
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        self.update_login_time()
        return jsonify ({"message": 'soemthign bozxjfsdzfas'}), 200
    
    def signup(self):
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.json.get('name'),
            "email": request.json.get('email'),
            # "password": pbkdf2_sha256.encrypt(request.json.get('password')),
            "image": None,
            "password": bcrypt.hashpw(request.json.get('password').encode('utf-8'), bcrypt.gensalt()),  
            "created_date": datetime.datetime.utcnow(),
            "last_update_time": datetime.datetime.utcnow(),
            "last_login_time": None
            
        }

        # Check for existing users
        if db.users.find_one({"email":user['email']}):
            return jsonify ({"error": 'Email address in use'}), 400
        
        if db.users.find_one({"name": user['name']}):
            return jsonify ({"error": 'user name address in use'}), 400
        
        users_collection = db['users']

    # Insert the user data into the 'users' collection
        if users_collection.insert_one( user ) :
            del user['password']
            return jsonify(user), 200
            # return self.start_session(user)
        
        return jsonify({'error': 'Signup failed'}), 400

    def signout(self):
        session.clear()
        return redirect('/')
    
    def login(self):
        user = db.users.find_one(
            {
                'email': request.json.get('email'),

            }
        )

        if user and bcrypt.checkpw(request.json.get('password').encode("utf-8"), user['password']):
            

            return self.start_session(user)
        # if user and pbkdf2_sha256.verify(request.json.get('password'), user['password']):
        #     return self.start_session(user)
        
        return  jsonify({'error' : 'Invalid Credintials'}), 401
    
    def upload_image(self):
        # if 
        return None

    def update_time(self):
        print(session["user"]["_id"])
        db.users.update_one (
            {"_id" : session["user"]["_id"]},
            {'$set': {'last_update_time' : datetime.datetime.utcnow()}}
        )
        return jsonify ({"message": 'Updated last update time for user'}), 200
    
    def update_login_time(self):
        print(session["user"]["_id"])
        db.users.update_one (
            {"_id" : session["user"]["_id"]},
            {'$set': {'last_login_time' : datetime.datetime.utcnow()}}
        )
        return jsonify ({"message": 'Updated last update time for user'}), 200

class insights:
    
    def get_outliers (self, column_name):
        return []
    
    def get_trends (self, column_name):
        return []
    
    def get_distributions (self, column_name):
        return []
    
    def get_basic_stats (self, column_name):
        return []
    
    def get_clusters (self, column_name):
        return []
    
    def get_rank (self, column_name):
        return []
    
    def get_derived_values (self, column_name):
        return []
    
    def get_associations (self, column_name):
        return []
    
    def get_differences (self, column_name):
        return []
    
    
    def generate_insights(self, column_name):
        all_insights[column_name] = {'outliers' : self.get_outliers(column_name) ,
                                     'derived values' : self.get_derived_values(column_name),
                                     'associations' : self.get_associations(column_name),
                                     'differences' : self.get_differences(column_name),
                                     'trends' : self.get_trends(column_name),
                                     'distribution' : self.get_distributions(column_name),
                                     'basic_stats' : self.get_basic_stats(column_name),
                                     'clusters' : self.get_clusters(column_name),
                                     'rank' : self.get_rank(column_name)}        

        
        #Make it a fair portion of all_insights and take care of errors when there isn't enough of certain number of insight-types
        session['current_insights'] = []
        ###################
        # Add to session variables the index of each insight-type that was added to current_insights 
        # Add to session variables the maximum index possible so that we know when to refresh for each type 
        
        ####################
        return session['current_insights']
