from flask import Flask, jsonify, request, session, redirect
from application import db
import bcrypt, datetime, uuid, json, random
import pandas as pd
import requests

class User:
    
    
    
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

    
class insights:
    all_insights = {}
    # Function to get outliers templates
    def get_outliers(self, column_name):
        return [
            f'The outliers in {column_name} are beyond the normal range. Notable outliers include {column_name} = {round(random.uniform(60, 80), 2)} and {column_name} = {round(random.uniform(120, 150), 2)}.',
            f'Identification of outliers in {column_name} suggests potential anomalies. Outlying values like {column_name} = {round(random.uniform(90, 110), 2)} and {column_name} = {round(random.uniform(160, 190), 2)} should be examined.',
            f'Outliers in {column_name} may impact the overall analysis. Values such as {column_name} = {round(random.uniform(75, 95), 2)} and {column_name} = {round(random.uniform(130, 160), 2)} stand out.'
        ]

    # Function to get trends templates
    def get_trends(self, column_name):
        return [
            f'{column_name} exhibits a noticeable upward trend over time, with values increasing from {round(random.uniform(20, 30), 2)} to {round(random.uniform(40, 50), 2)}.',
            f'The analysis of {column_name} indicates a consistent downward trend. Values have decreased steadily from {round(random.uniform(70, 80), 2)} to {round(random.uniform(50, 60), 2)}.',
            f'A significant upward trend is observed in {column_name}, with values rising from {round(random.uniform(30, 40), 2)} to {round(random.uniform(50, 60), 2)}.'
        ]

    # Function to get distributions templates
    def get_distributions(self, column_name):
        return [
            f'The distribution of {column_name} is positively skewed, as evidenced by values ranging from {round(random.uniform(10, 20),2)} to {round(random.uniform(30, 40),2)}.',
            f'A left-skewed distribution is evident in {column_name}, with values concentrated between {round(random.uniform(30, 40),2)} and {round(random.uniform(50, 60),2)}.',
            f'{column_name} displays a symmetrical distribution, with values evenly distributed around the mean ({round(random.uniform(40, 50),2)}).'
        ]

    # Function to get basic stats templates
    def get_basic_stats(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_columns = df.select_dtypes(include=['object', 'category', 'datetime64']).columns
        date_columns = df.select_dtypes(include=['datetime64']).columns
        units = {}
        for column in numerical_columns:
        ## TODO: fix the logic to change dates that are misflagged as ints or objects to datetime (include years, months, days,...) 
            # if df[column].dtype == 'int64' and 1400 <= df[column].min() <= df[column].max() <= 2100 and 'year' in column.lower():
            #     numerical_columns = numerical_columns[numerical_columns != column]
            #     date_columns.append(pd.Index([column]))
            #     pass
            try:
                tempUnits = column.split('(')[-1]
                if tempUnits[-1] == ')':
                    units[column] = tempUnits[:-1]

            except:
                pass
                

        insights = []
        if column_name in numerical_columns:
            stats = df.describe()[column_name]    
            if column_name in units.keys():
                insights += ['The mean of ' + column_name + ' is equal to ' + str(stats['mean']) + ' ' + units[column_name]]
                insights += ['The standard deviation of ' + column_name + ' is equal to ' + str(stats['std']) + ' ' + units[column_name]]
                insights += ['The minimum of ' + column_name + ' is equal to ' + str(stats['min']) + ' ' + units[column_name]]
                insights += ['The ' + column_name + ' at the 25th percentile is recorded as ' + str(stats['25%']) + ' ' + units[column_name]]
                insights += ['The ' + column_name + ' at the 50th percentile is recorded as ' + str(stats['50%']) + ' ' + units[column_name]]
                insights += ['The ' + column_name + ' at the 75th percentile is recorded as ' + str(stats['75%']) + ' ' + units[column_name]]
                insights += ['The maximum of ' + column_name + ' is equal to ' + str(stats['max']) + ' ' + units[column_name]]
                insights += ['The total ' + column_name + ' in this dataset, is equal to ' + str(df[column_name].sum()) + ' ' + units[column_name]]
            else:
                insights += ['The mean of ' + column_name + ' is equal to ' + str(stats['mean'])]
                insights += ['The standard deviation of ' + column_name + ' is equal to ' + str(stats['std'])]
                insights += ['The minimum of ' + column_name + ' is equal to ' + str(stats['min'])]
                insights += ['The ' + column_name + ' at the 25th percentile is recorded as ' + str(stats['25%'])]
                insights += ['The ' + column_name + ' at the 50th percentile is recorded as ' + str(stats['50%'])]
                insights += ['The ' + column_name + ' at the 75th percentile is recorded as ' + str(stats['75%'])]
                insights += ['The maximum of ' + column_name + ' is equal to ' + str(stats['max'])]
                insights += ['The total ' + column_name + ' in this dataset, is equal to ' + str(df[column_name].sum())]

        if column_name in categorical_columns:
            for numerical_column in numerical_columns:
                avg = df[numerical_column].mean()
                if numerical_column in units.keys():
                    insights += [f'The insident with maximum {numerical_column} happens when the {column_name} is {df.loc[df[numerical_column].idxmax()][column_name]}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']
                    insights += [f'The insident with minimum {numerical_column} happens when the {column_name} is {df.loc[df[numerical_column].idxmin()][column_name]}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

                    asum = df.groupby(column_name)[numerical_column].sum().reset_index()
                    insights += [f'The {column_name} with the most {numerical_column} is {asum.loc[asum[numerical_column].idxmax()][column_name]}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']

                    insights += [f'The {column_name} with the least {numerical_column} is {asum.loc[asum[numerical_column].idxmin()][column_name]}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

                    amean = df.groupby(column_name)[numerical_column].mean().reset_index()
                    insights += [f'The {column_name} with the highest average {numerical_column} is {amean.loc[amean[numerical_column].idxmax()][column_name]}, the highest average is {amean.loc[amean[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']

                    insights += [f'The {column_name} with the lowest average {numerical_column} is {amean.loc[amean[numerical_column].idxmin()][column_name]}, the lowest average is {amean.loc[amean[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

                    std = df.groupby(column_name)[numerical_column].std().reset_index()
                    insights += [f'The {column_name} with the highest standard deviation in {numerical_column} is {std.loc[std[numerical_column].idxmax()][column_name]}, the standard deviation is {std.loc[std[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']

                    insights += [f'The {column_name} with the lowest standard deviation in {numerical_column} is {std.loc[std[numerical_column].idxmin()][column_name]}, the standard deviation is {std.loc[std[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']
                else:

                    insights += [f'The insident with maximum {numerical_column} happens when the {column_name} is {df.loc[df[numerical_column].idxmax()][column_name]}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmax()][numerical_column]}']
                    insights += [f'The insident with minimum {numerical_column} happens when the {column_name} is {df.loc[df[numerical_column].idxmin()][column_name]}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmin()][numerical_column]}']

                    asum = df.groupby(column_name)[numerical_column].sum().reset_index()
                    insights += [f'The {column_name} with the most {numerical_column} is {asum.loc[asum[numerical_column].idxmax()][column_name]}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmax()][numerical_column]}']

                    insights += [f'The {column_name} with the least {numerical_column} is {asum.loc[asum[numerical_column].idxmin()][column_name]}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmin()][numerical_column]}']

                    amean = df.groupby(column_name)[numerical_column].mean().reset_index()
                    insights += [f'The {column_name} with the highest average {numerical_column} is {amean.loc[amean[numerical_column].idxmax()][column_name]}, the highest average is {amean.loc[amean[numerical_column].idxmax()][numerical_column]}']

                    insights += [f'The {column_name} with the lowest average {numerical_column} is {amean.loc[amean[numerical_column].idxmin()][column_name]}, the lowest average is {amean.loc[amean[numerical_column].idxmin()][numerical_column]}']

                    std = df.groupby(column_name)[numerical_column].std().reset_index()
                    insights += [f'The {column_name} with the highest standard deviation in {numerical_column} is {std.loc[std[numerical_column].idxmax()][column_name]}, the standard deviation is {std.loc[std[numerical_column].idxmax()][numerical_column]}']

                    insights += [f'The {column_name} with the lowest standard deviation in {numerical_column} is {std.loc[std[numerical_column].idxmin()][column_name]}, the standard deviation is {std.loc[std[numerical_column].idxmin()][numerical_column]}']

        return insights 

    # [
    #         f'The mean value of {column_name} is {round(random.uniform(30, 40),2)}. This indicates the central tendency of the data.',
    #         f'The standard deviation of {column_name} is {round(random.uniform(10, 15),2)}. A lower standard deviation suggests less variability in the data.'
    #     ]

    # Function to get clusters templates
    def get_clusters(self, column_name):
        return [
            f'Cluster analysis reveals distinct groups in {column_name}. Notable clusters include {column_name} = {random.choice(["A", "B", "C"])} and {column_name} = {random.choice(["X", "Y", "Z"])}.',
            f'Data points in {column_name} form identifiable clusters. Notable cluster centers are {column_name} = {round(random.uniform(40, 50), 2)} and {column_name} = {round(random.uniform(60, 70),2)}.',
            f'Analysis of {column_name} data using clustering techniques identifies distinct groups. Key clusters include {column_name} = {random.choice(["M", "N", "O"])} and {column_name} = {random.choice(["P", "Q", "R"])}.'
        ]

    # Function to get rank templates
    def get_rank(self, column_name):
        return [
            f'The rank of each category in {column_name} is [2, 4, 1, 0, 3]. Notable ranks include {column_name} = {random.choice(["A", "B", "C"])} at position 2.',
            f'{column_name} is ranked highest based on specific criteria. For example, {column_name} = {random.choice(["X", "Y", "Z"])} is the top-ranked category.',
            f'Ranking analysis reveals significant disparities among categories in {column_name}. Notable ranks include {column_name} = {random.choice(["D", "E", "F"])} at position 3.'
        ]

    # Function to get derived values templates
    def get_derived_values(self, column_name):
        return [
            f'Derived values from {column_name} provide additional insights. For instance, consider the derived value {column_name} = {round(random.uniform(40, 50),2)}.',
            f'{column_name} derived values contribute to the overall analysis. A notable derived value is {column_name} = {round(random.uniform(60, 70),2)}.',
            f'Incorporating derived values enhances the understanding of {column_name}. Explore insights from values like {column_name} = {round(random.uniform(70, 80),2)}.'
        ]

    # Function to get associations templates
    def get_associations(self, column_name):
        return [
            f'There is a strong association between {column_name} and another variable. Notable associations include {column_name} = {round(random.uniform(30, 40),2)} and {column_name} = {round(random.uniform(50, 60),2)}.',
            f'Association analysis suggests a moderate relationship between {column_name} and another variable. Consider values like {column_name} = {round(random.uniform(70, 80),2)} and {column_name} = {round(random.uniform(90, 100),2)}.',
            f'Exploring associations with other variables reveals significant correlations. Notable associations include {column_name} = {round(random.uniform(40, 50),2)} with another variable.'
        ]

    # Function to get differences templates
    def get_differences(self, column_name):
        return [
            f'The differences in {column_name} across groups are statistically significant. Notable differences exist between groups with {column_name} = {random.choice(["A", "B", "C"])} and {column_name} = {random.choice(["X", "Y", "Z"])}.',
            f'Significant differences exist in {column_name} between different categories. Notable differences are observed between {column_name} = {random.choice(["M", "N", "O"])} and {column_name} = {random.choice(["P", "Q", "R"])}.',
            f'Differences in {column_name} are evident when comparing groups with {column_name} = {random.choice(["D", "E", "F"])} and {column_name} = {random.choice(["G", "H", "I"])}.'
        ]
    
    def generate_insights(self, column_name, prev_insights, insight_count):
        insights = {
            # 'outliers' : self.get_outliers(column_name) ,
            #                             'derived values' : self.get_derived_values(column_name),
            #                             'associations' : self.get_associations(column_name),
            #                             'differences' : self.get_differences(column_name),
            #                             'trends' : self.get_trends(column_name),
            #                             'distribution' : self.get_distributions(column_name),
                                        'basic_stats' : self.get_basic_stats(column_name)
                                        # ,
                                        # 'clusters' : self.get_clusters(column_name),
                                        # 'rank' : self.get_rank(column_name)
                                        }        

        
        #Make sure that each returned insight is unvisited
        all_values = ([value for values in insights.values() for value in values])
        if len(all_values) <= insight_count:
            return jsonify({'insights' :all_values})
        
        new_insights_count = min(insight_count,len(all_values) - len(prev_insights))
                
        current_insights = random.sample([v for v in all_values if v not in prev_insights], new_insights_count)
        
        if new_insights_count >= insight_count:
            prev_insights.extend(current_insights)
        if new_insights_count < insight_count:
            print (current_insights)
            if prev_insights != []:
                current_insights.extend(random.sample(prev_insights, insight_count - len(current_insights)))
                prev_insights = []
        
        
        return jsonify({'insights' : current_insights, 'prev_insights' : prev_insights, 'count' : new_insights_count})
            
        
            #Make it a fair portion of all_insights and take care of errors when there isn't enough of certain number of insight-types
        ###################
        # Add to session variables the index of each insight-type that was added to current_insights 
        # Add to session variables the maximum index possible so that we know when to refresh for each type 
        
        ####################
    

            
    def get_insights(self):
        column_name = request.json.get('column_name')
        prev_insights = request.json.get('prev_insights')
        insight_count = request.json.get('insight_count')
        
        if not prev_insights:
            prev_insights = []
        # column_name = json.loads(request.args.get('json_data')).get('column_name')
        # Check if column_name already has insights in the session/db
        ########
        #IF BLOCK
        ########
        #ELSE BLOCK 
  
        return self.generate_insights(column_name, prev_insights, insight_count)
        ########
        
        
class hypothesis:
    
    def get_hypothesis(self):
        column_name = request.json.get('column_name')
        insights = request.json.get('insights')
        context = request.json.get('context')
        insights.append(context)
        prompts = insights
        
        API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
        headers = {"Authorization": "Bearer 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"} 
        
        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        
        history = []
        data = []
        
        for prompt in prompts:
            output = query({
                "inputs": "Respond to the Current Input using the past user inputs below.\nUser Inputs: " + str(history) + "\nCurrent Input: " + prompt + "\nAnswer:",
                "parameters": {
                    "return_full_text": False,
                    "max_time": 2.0
                    }
            })
            history.append(prompt)
            if len(history) > 15:
                history.pop(0)
            try:
                data.append(output[0]['generated_text'])
            except KeyError as e:
                data.append("Error with following prompt: " + prompt)
        return jsonify({'data' : data})
