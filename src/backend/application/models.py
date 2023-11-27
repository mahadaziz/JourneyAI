from flask import Flask, jsonify, request, session, redirect
from application import db
import bcrypt, datetime, uuid, json, random

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
    all_insights = {}
    def get_outliers (self, column_name):
        return [f'{column_name} outlier 1', f'{column_name} outlier 2']
    
    def get_trends (self, column_name):
        return [f'{column_name} trend 1', f'{column_name} trend 2']
    
    def get_distributions (self, column_name):
        return [f'{column_name} distribution 1', f'{column_name} distribution 2']
    
    def get_basic_stats (self, column_name):
        return [f'{column_name} basic stat 1', f'{column_name} basic stat 2']
    
    def get_clusters (self, column_name):
        return [f'{column_name} cluster 1', f'{column_name} cluster 2']
    
    def get_rank (self, column_name):
        return [f'{column_name} rank 1', f'{column_name} rank 2']
    
    def get_derived_values (self, column_name):
        return [f'{column_name} derived values 1', f'{column_name} derived values 2']
    
    def get_associations (self, column_name):
        return [f'{column_name} associations 1', f'{column_name} associations 2']
    
    def get_differences (self, column_name):
        return [f'{column_name} differences 1', f'{column_name} differences 2']
    
    
    def generate_insights(self, column_name):
        if 'insights' not in session:
    
            self.all_insights[column_name] = {'outliers' : self.get_outliers(column_name) ,
                                        'derived values' : self.get_derived_values(column_name),
                                        'associations' : self.get_associations(column_name),
                                        'differences' : self.get_differences(column_name),
                                        'trends' : self.get_trends(column_name),
                                        'distribution' : self.get_distributions(column_name),
                                        'basic_stats' : self.get_basic_stats(column_name),
                                        'clusters' : self.get_clusters(column_name),
                                        'rank' : self.get_rank(column_name)}        

            session['insights'] = self.all_insights
            session['insights']['prev_insights'] = {}
            session['insights']['prev_insights'][column_name] =  []
        else:
            session['insights'][column_name] = {'outliers' : self.get_outliers(column_name) ,
                                        'derived values' : self.get_derived_values(column_name),
                                        'associations' : self.get_associations(column_name),
                                        'differences' : self.get_differences(column_name),
                                        'trends' : self.get_trends(column_name),
                                        'distribution' : self.get_distributions(column_name),
                                        'basic_stats' : self.get_basic_stats(column_name),
                                        'clusters' : self.get_clusters(column_name),
                                        'rank' : self.get_rank(column_name)} 
        if 'prev_insights' not in session['insights']:
            session['insights']['prev_insights'] = {}
            session['insights']['prev_insights'][column_name] =  []
        if column_name not in session['insights']['prev_insights']:
            session['insights']['prev_insights'][column_name] =  []
            #Make it a fair portion of all_insights and take care of errors when there isn't enough of certain number of insight-types
        ###################
        # Add to session variables the index of each insight-type that was added to current_insights 
        # Add to session variables the maximum index possible so that we know when to refresh for each type 
        
        ####################
        return self.get_current_insights(column_name)
    
    def get_current_insights(self, column_name):
        all_values = ([value for values in session['insights'][column_name].values() for value in values])
        if len(all_values) <= 10:
            return jsonify({'insights' :all_values})
        
        new_insights_count = min(10,len(all_values) - len(session['insights']['prev_insights'][column_name]))
        
        prev_insights = session['insights']['prev_insights'][column_name]
        
        current_insights = random.sample([v for v in all_values if v not in prev_insights], new_insights_count)
        
        session['insights']['prev_insights'][column_name].extend(current_insights)
        if new_insights_count < 10:
            print (current_insights)
            current_insights.extend(random.sample(prev_insights, 10 - len(current_insights)))
            session['insights']['prev_insights'][column_name] = []
        
        
        return jsonify({'insights' : current_insights})
            
    def get_insights(self):
        column_name = request.json.get('column_name')
        # column_name = json.loads(request.args.get('json_data')).get('column_name')
        # Check if column_name already has insights in the session/db
        ########
        #IF BLOCK
        ########
        #ELSE BLOCK 
        if 'insights' not in session:
            return self.generate_insights(column_name)
        if column_name not in session['insights'].keys():
            return self.generate_insights(column_name)
        
        return self.get_current_insights(column_name)
        ########