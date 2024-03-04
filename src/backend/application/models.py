from flask import Flask, jsonify, request, session, redirect
from application import db
import bcrypt, datetime, uuid, json, random
import pandas as pd
import requests
from scipy.stats import zscore, skew, stats, linregress
from sklearn.cluster import KMeans
import numpy as np
import random

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
    
    def is_year_or_date_column(column, column_name):
        date_time_keywords = ['year', 'date', 'time', 'month', 'day']

        if column.dtype in ['int64', 'float64']:
            if any(keyword in column_name.lower() for keyword in date_time_keywords) and all(1000 <= x <= 3000 for x in column.dropna()):
                return True
        # try:
        #     pd.to_datetime(column, errors='coerce').notna().any()
        #     return True
        # except:
        #     pass
        return False

    cursor = db['cars'].find()
    df = pd.DataFrame(iter(cursor))
    df = df.drop(['_id'], axis=1)

    #global NUMERICAL_COLUMNS, CATEGORICAL_COLUMNS, DATE_LIKE_COLUMNS

    NUMERICAL_COLUMNS = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    CATEGORICAL_COLUMNS = df.select_dtypes(include=['object', 'category']).columns.tolist()
    DATE_LIKE_COLUMNS = ['model year']

    for col in df.columns:
        if is_year_or_date_column(df[col], col):
            DATE_LIKE_COLUMNS.append(col)
            if col in NUMERICAL_COLUMNS:
                NUMERICAL_COLUMNS.remove(col)
            if col in CATEGORICAL_COLUMNS:
                CATEGORICAL_COLUMNS.remove(col)

    def get_outliers(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        # Combine categorical and date-like columns for analysis
        combined_categorical_columns = self.CATEGORICAL_COLUMNS + self.DATE_LIKE_COLUMNS

        # Check if column exists
        if column_name not in df.columns:
            return []

        insights = []
        if column_name in self.NUMERICAL_COLUMNS:
            # Filter out null values from the column for outlier detection
            col_df = df[column_name].dropna()
            
            if len(col_df) == 0:
                return []
            
            Q1 = col_df.quantile(0.25)
            Q3 = col_df.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - (1.5 * IQR)
            upper_bound = Q3 + (1.5 * IQR)

            largest = (col_df > upper_bound)
            smallest = (col_df < lower_bound)
            
            outliers = col_df[largest | smallest]
            
            total = len(outliers)
            
            unit = ""
            for i in range(len(column_name)):
                if column_name[i] == "(":
                    unit = column_name[i:]

            if total > 0:
                max_outlier = outliers.max()
                min_outlier = outliers.min()
                percent = (total / len(col_df)) * 100
                insights.append(f'Found {total} outliers in {column_name}, around {percent:.2f}% of the data.')
                insights.append(f'The largest outlier in {column_name} is {max_outlier} {unit}.')                
                insights.append(f'The smallest outlier in {column_name} is {min_outlier} {unit}.')

                for col in combined_categorical_columns + self.NUMERICAL_COLUMNS:
                    if col != column_name:
                        col_max = df.loc[df[column_name] == max_outlier, col]
                        col_min = df.loc[df[column_name] == min_outlier, col]
                        maxrepeat = []
                        minrepeat = []
                        for val in col_max:
                            if val not in maxrepeat:
                                insights.append(f'The {col} corresponding to the largest outlier in {column_name} is {val}, at {max_outlier} {unit}.')
                                maxrepeat.append(val)
                        for val in col_min:
                            if val not in minrepeat:
                                insights.append(f'The {col} corresponding to the smallest outlier in {column_name} is {val}, at {min_outlier} {unit}.')
                                minrepeat.append(val)
        return insights

    # Function to get trends templates

    def get_trends(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []

        # Check if column exists
        if column_name not in df.columns:
            return []

        if column_name in self.DATE_LIKE_COLUMNS:
            df_sorted = df.sort_values(by=column_name)
            segments = df_sorted[column_name].dropna().unique()
            
            for i in range(len(segments) - 1):
                curr_segment = segments[i]
                next_segment = segments[i + 1]

                for num_col in self.NUMERICAL_COLUMNS:
                    curr_seg_val = df_sorted[df_sorted[column_name] == curr_segment][num_col].mean()
                    next_seg_val = df_sorted[df_sorted[column_name] == next_segment][num_col].mean()
                    
                    if next_seg_val > curr_seg_val:
                        segment_trend = "upward"
                    else:
                        segment_trend = "downward"
                        
                    insights.append(f"From {curr_segment} to {next_segment} in {column_name}, {num_col} shows a {segment_trend} trend.")

                for cat_col in self.CATEGORICAL_COLUMNS:
                    curr_seg_most = df_sorted[df_sorted[column_name] == curr_segment][cat_col].value_counts().idxmax()
                    next_seg_most = df_sorted[df_sorted[column_name] == next_segment][cat_col].value_counts().idxmax()
                    
                    if curr_seg_most != next_seg_most:
                        insights.append(f"From {curr_segment} to {next_segment} in {column_name}, the most frequent {cat_col} goes from {curr_seg_most} to {next_seg_most}.")

        # Trend Analysis for Numerical Columns
        if column_name in self.NUMERICAL_COLUMNS:
            if df[column_name].iloc[-1] > df[column_name].iloc[0]:
                overall_trend_direction = "upward"  
            else:
                overall_trend_direction = "downward"

            insights.append(f"Overall, {column_name} shows a {overall_trend_direction} trend.")

            # Analyze parallel and inverse trends with other numerical columns
            for other_col in self.NUMERICAL_COLUMNS:
                if other_col != column_name:
                    if df[other_col].iloc[-1] > df[other_col].iloc[0]:
                        other_col_trend = "upward"  
                    else: 
                        other_col_trend = "downward"
                    if overall_trend_direction == other_col_trend:
                        trend_relation = "parallel"  
                    else: 
                        trend_relation = "inverse"
                    insights.append(f"Overall, '{column_name}' and '{other_col}' have a {trend_relation} trend.")

            #TODO: Also add this separately outside of the for loop so the function works for date-like
            # Trend Analysis within Date-Like Column Segments
            for date_col in self.DATE_LIKE_COLUMNS:
                df_sorted = df.sort_values(by=date_col)
                segments = df_sorted[date_col].dropna().unique()

                for i in range(len(segments) - 1):
                    curr_segment = segments[i]
                    next_segment = segments[i + 1]
                    
                    # Correcting the references to use df_sorted for consistency
                    curr_seg_val = df_sorted[df_sorted[date_col] == curr_segment][column_name].iloc[0]
                    next_seg_value = df_sorted[df_sorted[date_col] == next_segment][column_name].iloc[0]
                    
                    if next_seg_value > curr_seg_val:
                        segment_trend = "upward"  
                    else: 
                        segment_trend = "downward"
                    
                    insights.append(f"The trend from {curr_segment} to {next_segment} in {column_name} is {segment_trend}, going from {curr_seg_val} to {next_seg_value}.")
                    # Analyzing trend relation within segments
                    for other_col in self.NUMERICAL_COLUMNS:
                        if other_col != column_name:
                            other_curr_seg_val = df_sorted[df_sorted[date_col] == curr_segment][other_col].iloc[0]
                            other_next_seg_val = df_sorted[df_sorted[date_col] == next_segment][other_col].iloc[0]
                            
                            if other_next_seg_val > other_curr_seg_val:
                                other_segment_trend = "upward" 
                            else: 
                                other_segment_trend = "downward"
                            if segment_trend == other_segment_trend:
                                trend_relation = "parallel" 
                            else: 
                                trend_relation = "inverse"
                            insights.append(f"In the transition from {curr_segment} to {next_segment}, {column_name} and {other_col} exhibit a {trend_relation} trend.")
        #TODO: Potentially make this categorical only as you will make date-like separate, see above
        # Trend Analysis for Categorical Columns
        elif column_name in self.CATEGORICAL_COLUMNS:
            for date_col in self.DATE_LIKE_COLUMNS:
                grouped_data = df.groupby([date_col, column_name]).size().reset_index(name='count')
                sorted_grouped_data = grouped_data.sort_values(by=date_col)

                prev_most_freq_category = None
                for _, group in sorted_grouped_data.groupby(date_col):
                    current_date = group[date_col].iloc[0]
                    most_freq_category = group.loc[group['count'].idxmax()][column_name]

                    if most_freq_category != prev_most_freq_category:
                        if prev_most_freq_category is not None:
                            insights.append(f"For '{date_col}' period starting {current_date}, {most_freq_category} is the new most frequent instance of {column_name}, going from {prev_most_freq_category}.")
                        else:
                            insights.append(f"For '{date_col}' period starting {current_date}, {most_freq_category} is the new most frequent instance of {column_name}.")
                        prev_most_freq_category = most_freq_category

        return insights

    # Function to get distributions templates

    #TODO: MODIFY
    def get_distributions(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []

        if column_name not in df.columns:
            return []

        non_null_data = df[column_name].dropna()

        if column_name in self.NUMERICAL_COLUMNS:
            column_skewness = skew(non_null_data)
            if column_skewness > 0.5:
                skew_type = "very positively (right)"
                insights.append(f"{column_name} was found to be {skew_type} skewed, indicating that few unusually large values above the average may be having a large impact.")
                threshold = non_null_data.mean() + 2 * non_null_data.std()   
            # elif column_skewness > 0.5:
            #     skew_type = "slightly positively (right)"
            #     insights.append(f"{column_name} was found to be {skew_type} skewed, indicating that few unusually large values above the average may be having a small impact.")
            # elif column_skewness <= 0.5 and column_skewness >= -0.5:
            #     skew_type = "normally"
            #     insights.append(f"{column_name} was found to be {skew_type} skewed, indicating most values are around the mean, as expected.")
            # elif column_skewness < -0.5:
            #     skew_type = "slightly negatively (left)"
            #     insights.append(f"{column_name} was found to be {skew_type} skewed, indicating that few unusually small values below the average may be having a small impact.")
            elif column_skewness < 0.5: 
                skew_type = "very negatively (left)"
                insights.append(f"{column_name} was found to be {skew_type} skewed, indicating that few unusually small values below the average may be having a large impact.")
                threshold = non_null_data.mean() - 2 * non_null_data.std()
            else:
                return []
            
            for col in self.CATEGORICAL_COLUMNS + self.DATE_LIKE_COLUMNS + self.NUMERICAL_COLUMNS:
                if col != column_name:
                    if column_skewness > 0.5:
                        col_max = df.loc[df[column_name] > threshold, col].dropna()
                        for val in col_max.unique():
                            insights.append(f'The value in {col} that could be leading to a positive skew in {column_name} is {val}.')
                    elif column_skewness < 0.5:
                        col_min = df.loc[df[column_name] < threshold, col].dropna()
                        for val in col_min.unique():
                            insights.append(f'The value in {col} that could be leading to a negative skew in {column_name} is {val}.')
        return insights

    #TODO: MODIFY
    # Function to get basic stats templates
    def get_basic_stats(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category', 'datetime64']).columns.tolist()
        categorical_columns = [ name for name in  categorical_columns if name != '_id' ]
        numerical_columns = [ name for name in  numerical_columns if name != '_id' ]
        # date_columns = df.select_dtypes(include=['datetime64']).columns
        units = {}
        for column in numerical_columns:
        ## TODO: fix the logic to change dates that are misflagged as ints or objects to datetime (include years, months, days,...) 
            if df[column].dtype == 'int64' and 1400 <= df[column].min() <= df[column].max() <= 2100 and 'year' in column.lower():
                numerical_columns = [name for name in numerical_columns if name != column]
                categorical_columns.append(column)
                df[column] = df[column].astype(int)
               
                pass
        ## The above should be commented out and date_columns should be created (I uncommented it for now because it will remove some bogus results)
            try:
                tempUnits = column.split('(')[-1]
                if tempUnits[-1] == ')':
                    units[column] = tempUnits[:-1]

            except:
                pass
        print(categorical_columns, numerical_columns)        

        insights = []
        if column_name in numerical_columns:
            stats = df.describe()[column_name].round(2)    
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
                # avg = df[numerical_column].mean()
                if numerical_column in units.keys():
                    category = df.loc[df[numerical_column].idxmax()][column_name]
                    insights += [f'The insident with maximum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']
                    category = df.loc[df[numerical_column].idxmin()][column_name]
                    insights += [f'The insident with minimum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

                    asum = df.groupby(column_name)[numerical_column].sum().reset_index()
                    
                    category = asum.loc[asum[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the most {numerical_column} is {int(category) if isinstance(category, float) else category}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']
                    
                    category = asum.loc[asum[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the least {numerical_column} is {int(category) if isinstance(category, float) else category}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

                    amean = df.groupby(column_name)[numerical_column].mean().reset_index()
                    
                    category = amean.loc[amean[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the highest average {numerical_column} is {int(category) if isinstance(category, float) else category}, the highest average is {amean.loc[amean[numerical_column].idxmax()][numerical_column]:.2f} {units[numerical_column]}']

                    category = amean.loc[amean[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the lowest average {numerical_column} is {int(category) if isinstance(category, float) else category}, the lowest average is {amean.loc[amean[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

                    std = df.groupby(column_name)[numerical_column].std().reset_index()
                    category = std.loc[std[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the highest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmax()][numerical_column]:.2f} {units[numerical_column]}']

                    category = std.loc[std[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the lowest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmin()][numerical_column]:.2f} {units[numerical_column]}']
                else:
                    category = df.loc[df[numerical_column].idxmax()][column_name]
                    insights += [f'The insident with maximum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmax()][numerical_column]}']

                    category = df.loc[df[numerical_column].idxmin()][column_name]
                    insights += [f'The insident with minimum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmin()][numerical_column]}']

                    asum = df.groupby(column_name)[numerical_column].sum().reset_index()
                    
                    category =  asum.loc[asum[numerical_column].idxmax()][column_name]                   
                    insights += [f'The {column_name} with the most {numerical_column} is {int(category) if isinstance(category, float) else category}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmax()][numerical_column]}']

                    category = asum.loc[asum[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the least {numerical_column} is {int(category) if isinstance(category, float) else category}, the sum of {numerical_column} is {asum.loc[asum[numerical_column].idxmin()][numerical_column]}']

                    amean = df.groupby(column_name)[numerical_column].mean().reset_index()
                    category = amean.loc[amean[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the highest average {numerical_column} is {int(category) if isinstance(category, float) else category}, the highest average is {amean.loc[amean[numerical_column].idxmax()][numerical_column]:.2f}']
                    category = amean.loc[amean[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the lowest average {numerical_column} is {int(category) if isinstance(category, float) else category}, the lowest average is {amean.loc[amean[numerical_column].idxmin()][numerical_column]}']

                    std = df.groupby(column_name)[numerical_column].std().reset_index()
                    category = std.loc[std[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the highest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmax()][numerical_column]:.2f}']

                    category = std.loc[std[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the lowest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmin()][numerical_column]:.2f}']

        return insights
 

    # [
    #         f'The mean value of {column_name} is {round(random.uniform(30, 40),2)}. This indicates the central tendency of the data.',
    #         f'The standard deviation of {column_name} is {round(random.uniform(10, 15),2)}. A lower standard deviation suggests less variability in the data.'
    #     ]

    # Function to get clusters templates
    
    # #TODO:REMOVE ALL CLUSTER
    # def get_clusters(self, column_name):
    #     cursor = db['cars'].find()
    #     df = pd.DataFrame(iter(cursor))
    #     if column_name not in self.NUMERICAL_COLUMNS:
    #         return []

    #     # Remove NaN values from the column
    #     clean_df = df.dropna(subset=[column_name])

    #     # Determine the optimal number of clusters using the Elbow Method
    #     optimal_k = self.find_optimal_clusters(clean_df[[column_name]])
    #     if optimal_k is None:
    #         return []

    #     # Perform clustering with the optimal number of clusters
    #     kmeans = KMeans(n_clusters=optimal_k)
    #     kmeans.fit(clean_df[[column_name]])
    #     clean_df['cluster'] = kmeans.labels_

    #     # Generate insights
    #     insights = self.generate_cluster_insights(clean_df, column_name, optimal_k)

    #     return insights

    # def find_optimal_clusters(self, data):
    #     distortions = []
    #     K = range(1, 10)  # Testing 1 to 9 clusters
    #     for k in K:
    #         kmeanModel = KMeans(n_clusters=k)
    #         kmeanModel.fit(data)
    #         distortions.append(kmeanModel.inertia_)

    #     # Find the elbow point
    #     k_distances = np.diff(distortions)
    #     second_derivative = np.diff(k_distances)
    #     elbow_point = np.argmax(second_derivative) + 2  # +2 due to double differencing
    #     if elbow_point > 0 and elbow_point < len(K):
    #         return elbow_point
    #     return None
    
    # def generate_cluster_insights(self, df, column_name, num_clusters):
    #     insights = []

    #     # Characteristics of Clusters in the Chosen Column
    #     for cluster in sorted(df['cluster'].unique()):
    #         cluster_mean = df[df['cluster'] == cluster][column_name].mean()
    #         insights.append(f'{num_clusters} clusters found in {column_name}. Cluster {cluster} has an average value of {cluster_mean:.2f}.')

    #     # Correlation with Other Numerical Columns
    #     for other_col in self.NUMERICAL_COLUMNS:
    #         if other_col != column_name:
    #             for cluster in sorted(df['cluster'].unique()):
    #                 cluster_mean = df[df['cluster'] == cluster][column_name].mean()
    #                 mean_value = df[df['cluster'] == cluster][other_col].mean()
    #                 insights.append(f'Cluster {cluster} (avg {column_name}: {cluster_mean:.2f}) correlates with an average {other_col} value of {mean_value:.2f}')

    #     # Interaction with Categorical Columns
    #     for cat_col in self.CATEGORICAL_COLUMNS:
    #         for cluster in sorted(df['cluster'].unique()):
    #             cluster_mean = df[df['cluster'] == cluster][column_name].mean()
    #             most_common_category = df[df['cluster'] == cluster][cat_col].mode()[0]
    #             insights.append(f'In Cluster {cluster} (avg {column_name}: {cluster_mean:.2f}), the most common category in {cat_col} is {most_common_category}')

    #     # Insights on Outliers Within Clusters
    #     for cluster in sorted(df['cluster'].unique()):
    #         cluster_data = df[df['cluster'] == cluster][column_name]
    #         cluster_mean = cluster_data.mean()
    #         std_dev = cluster_data.std()
    #         lower_bound = cluster_mean - 2 * std_dev
    #         upper_bound = cluster_mean + 2 * std_dev
    #         outliers = df[(df['cluster'] == cluster) & ((df[column_name] < lower_bound) | (df[column_name] > upper_bound))]
    #         insights.append(f'Cluster {cluster} (avg {column_name}: {cluster_mean:.2f}) has {len(outliers)} outliers. This might indicate special cases or anomalies within this group.')

    #     return insights

    #TODO: MODIFY
    # Function to get rank templates
    def get_rank(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []

        if column_name not in df.columns:
            return []

        if column_name in self.CATEGORICAL_COLUMNS:
            for num_col in self.NUMERICAL_COLUMNS:
                ranked = df.groupby(column_name)[num_col].mean().sort_values(ascending=False)
                top_ranks = ranked.head(3).index.tolist()
                bottom_ranks = ranked.tail(3).index.tolist()
                bottom_ranks.reverse()
                top_rank_str = ', '.join(f"'{val}'" for val in top_ranks[:min(3, len(ranked))])
                bottom_rank_str = ', '.join(f"'{val}'" for val in bottom_ranks[-min(3, len(ranked)):])

                insights.append(f"In '{column_name}', {top_rank_str} rank highest based on '{num_col}'.")
                insights.append(f"In '{column_name}', {bottom_rank_str} rank lowest based on '{num_col}'.")

        elif column_name in self.NUMERICAL_COLUMNS or column_name in self.DATE_LIKE_COLUMNS:
            for cat_col in self.CATEGORICAL_COLUMNS:
                ranked = df.groupby(cat_col)[column_name].mean().sort_values(ascending=False)
                top_ranks = ranked.head(3).index.tolist()
                bottom_ranks = ranked.tail(3).index.tolist()
                bottom_ranks.reverse()
                top_rank_str = ', '.join(f"'{val}'" for val in top_ranks[:min(3, len(ranked))])
                bottom_rank_str = ', '.join(f"'{val}'" for val in bottom_ranks[-min(3, len(ranked)):])

                insights.append(f"Based on '{column_name}', values {top_rank_str} from '{cat_col}' rank highest.")
                insights.append(f"Based on '{column_name}', values {bottom_rank_str} from '{cat_col}' rank lowest.")

        return insights

    #TODO:MODIFY
    # Function to get associations templates
    def get_associations(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []

        if column_name not in df.columns:
            return []

        # Correlation Insights Between Numerical Columns
        if column_name in self.NUMERICAL_COLUMNS:
            for other_col in self.NUMERICAL_COLUMNS:
                if other_col != column_name:
                    # Synchronize non-null data between the two columns
                    non_null_indices = df[column_name].notnull() & df[other_col].notnull()
                    valid_data = df[non_null_indices][[column_name, other_col]]

                    if len(valid_data) > 1:
                        correlation, _ = stats.pearsonr(valid_data[column_name], valid_data[other_col])
                        correlation_type = 'positive' if correlation > 0 else 'negative'
                        if abs(correlation) > 0.5:  # Strong correlation threshold
                            insights.append(f"There appears to be a strong {correlation_type} correlation between '{column_name}' and '{other_col}', suggesting that as one increases, the other also increases/decreases.")

            # Association with Categorical Columns
            for cat_col in self.CATEGORICAL_COLUMNS:
                category_means = df.groupby(cat_col)[column_name].mean()
                highest_mean_category = category_means.idxmax()
                lowest_mean_category = category_means.idxmin()
                insights.append(f"There's a notable association between '{column_name}' and '{cat_col}', where '{highest_mean_category}' consistently aligns with higher values and '{lowest_mean_category}' with lower values.")
        
        # Association Insights for a Categorical Column
        elif column_name in self.CATEGORICAL_COLUMNS:
            for num_col in self.NUMERICAL_COLUMNS:
                valid_data = df.dropna(subset=[column_name, num_col])
                category_means = valid_data.groupby(column_name)[num_col].mean()
                top_category = category_means.idxmax()
                insights.append(f"Analysis shows that different categories in '{column_name}' have significantly different average values in {num_col}, particularly {top_category} with the highest average.")

                # Association of specific categories with higher/lower numerical values
                for category in valid_data[column_name].unique():
                    mean_value = valid_data[valid_data[column_name] == category][num_col].mean()
                    insights.append(f"There's a notable association between '{column_name}' and '{num_col}', where '{category}' consistently aligns with {'higher' if mean_value > valid_data[num_col].mean() else 'lower'} values.")

            # Association with Other Categorical Columns
            for cat_col in self.CATEGORICAL_COLUMNS:
                if cat_col != column_name:
                    contingency_table = pd.crosstab(df[column_name], df[cat_col])
                    top_combination = contingency_table.unstack().idxmax()
                    insights.append(f"Certain combinations of categories from '{column_name}' and '{cat_col}' occur more frequently than others, especially between '{top_combination[0]}' and '{top_combination[1]}'.")

        return insights

    # #TODO: REMOVE
    # # Function to get differences templates
    # def get_differences(self, column_name):
    #     cursor = db['cars'].find()
    #     df = pd.DataFrame(iter(cursor))

    #     insights = []
    #     if column_name in df.columns and df[column_name].dtype in ['int64', 'float64']:
    #         categorical_columns = df.select_dtypes(include=['object', 'category']).columns

        
    #         # 2. Differences in Relation to Categorical Columns
    #         for cat_column in categorical_columns:
    #             if cat_column != column_name:
    #                 grouped_diff = df.groupby(cat_column)[column_name].mean()
    #                 #insights.append(f'Differences in {column_name} are observed when grouped by {cat_column}. Average values per group: {grouped_diff.to_dict()}.')

    #         # 3. Specific Examples
    #         for cat_column in categorical_columns:
    #             if cat_column != column_name:
    #                 sample_groups = df.groupby(cat_column).apply(lambda x: x.sample(1)).reset_index(drop=True).head(3)
    #                 for _, row in sample_groups.iterrows():
    #                     example_insight = f'For example, in the {cat_column} group "{row[cat_column]}", the value of {column_name} is {row[column_name]:.2f}.'
    #                     #insights.append(example_insight)

    #     return insights
    
    # Function to get graphable insights
    def graph_insights(self, column_name, prev_insights, insight_count):
        import random
        insights = {}
        insight_count = min(insight_count, len(self.NUMERICAL_COLUMNS)*3)
        if column_name in self.DATE_LIKE_COLUMNS:    
            while len(insights) < insight_count:
                for col in self.NUMERICAL_COLUMNS:
                    if random.randint(1,2) == 1 and len(insights) < insight_count :
                        cursor = (db.cars.find({col : {'$gt': 0}},{'_id': 0, column_name: 1, col: 1}))
                        df = pd.DataFrame(iter(cursor))
                        df.sort_values(by=column_name, inplace=True)
                        if random.randint(1,2) == 1 and len(insights) < insight_count and f'total "{col}"' not in ''.join(insights.keys()) :
                            
                            asum = df.groupby(column_name)[col].sum().reset_index()
                            slope, intercept, r_value, p_value, std_err = linregress(asum[column_name], asum[col])                
                            if np.abs(slope) < 0.05:  
                                insights[f'The total "{col}" is relatively constant across most {column_name}'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                            elif slope >= 0.05:
                                opposite_trend = []
                                for i in range(1, len(asum)):
                                    adate, value = asum.loc[i, [column_name, col]]
                                    prev_adate, prev_value = asum.loc[i-1, [column_name, col]]
                                    if value < prev_value:
                                        opposite_trend += [adate]
                                if len(opposite_trend) > len(asum)/3:
                                    insights[f'There is a notable level of variability in total "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                                elif len(opposite_trend) == 0:
                                    insights[f'In general, the overarching trend in total "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                                else:
                                    insights[f'In general, the overarching trend in total "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values. However, this upward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected dips. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                            else:
                                opposite_trend = []
                                for i in range(1, len(asum)):
                                    adate, value = asum.loc[i, [column_name, col]]
                                    prev_adate, prev_value = asum.loc[i-1, [column_name, col]]
                                    if value > prev_value:
                                        opposite_trend += [adate]
                                if len(opposite_trend) > len(asum)/3:
                                    insights[f'There is a notable level of variability in total "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                                elif len(opposite_trend) == 0:
                                    insights[f'In general, the overarching trend in total "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing a downward movement in values'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                                else:
                                    insights[f'In general, the overarching trend in total "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing an downward movement in values. However, this downward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected increase in value. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                        
                        if random.randint(1,2) == 1 and len(insights) < insight_count and f'average "{col}"' not in ''.join(insights.keys()) :
                            aavg = df.groupby(column_name)[col].mean().reset_index()
                            slope, intercept, r_value, p_value, std_err = linregress(aavg[column_name], aavg[col])                
                            if np.abs(slope) < 0.05:  
                                insights[f'The average "{col}" is relatively constant across most {column_name}'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                            elif slope >= 0.05:
                                opposite_trend = []
                                for i in range(1, len(aavg)):
                                    adate, value = aavg.loc[i, [column_name, col]]
                                    prev_adate, prev_value = aavg.loc[i-1, [column_name, col]]
                                    if value < prev_value:
                                        opposite_trend += [adate]
                                if len(opposite_trend) > len(aavg)/3:
                                    insights[f'There is a notable level of variability in average "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                                elif len(opposite_trend) == 0:
                                    insights[f'In general, the overarching trend in average "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                                else:
                                    insights[f'In general, the overarching trend in average "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values. However, this upward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected dips. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                            else:
                                opposite_trend = []
                                for i in range(1, len(aavg)):
                                    adate, value = aavg.loc[i, [column_name, col]]
                                    prev_adate, prev_value = aavg.loc[i-1, [column_name, col]]
                                    if value > prev_value:
                                        opposite_trend += [adate]
                                if len(opposite_trend) > len(aavg)/3:
                                    insights[f'There is a notable level of variability in average "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                                elif len(opposite_trend) == 0:
                                    insights[f'In general, the overarching trend in average "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing a downward movement in values'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                                else:
                                    insights[f'In general, the overarching trend in average "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing an downward movement in values. However, this downward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected increase in value. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name ,f'Average {col}', aavg.to_dict('records')]
                            
                        if random.randint(1,2) == 1 and len(insights) < insight_count and f'frequency of recorded entries for "{col}"' not in ''.join(insights.keys()) :
                            asize = df.groupby(column_name)[col].size().reset_index()
                            slope, intercept, r_value, p_value, std_err = linregress(asize[column_name], asize[col])                
                            if np.abs(slope) < 0.05:  
                                insights[f'The frequency of recorded entries for "{col}" is relatively constant across most {column_name}'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
                            elif slope >= 0.05:
                                opposite_trend = []
                                for i in range(1, len(asize)):
                                    adate, value = asize.loc[i, [column_name, col]]
                                    prev_adate, prev_value = asize.loc[i-1, [column_name, col]]
                                    if value < prev_value:
                                        opposite_trend += [adate]
                                if len(opposite_trend) > len(asize)/3:
                                    insights[f'There is a notable level of variability in the frequency of recorded entries for "{col}" greater than zero. This variability is characterized by alternating increases and decreases in value from one {column_name} to another'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
                                elif len(opposite_trend) == 0:
                                    insights[f'In general, the overarching trend in frequency of recorded entries for "{col}" greater than zero indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
                                else:
                                    insights[f'In general, the overarching trend in the frequency of recorded entries for "{col}" greater than zero indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values. However, this upward trend is punctuated by notable exceptions in specific  {column_name} , where we observe unexpected dips. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
                            else:
                                opposite_trend = []
                                for i in range(1, len(asize)):
                                    adate, value = asize.loc[i, [column_name, col]]
                                    prev_adate, prev_value = asize.loc[i-1, [column_name, col]]
                                    if value > prev_value:
                                        opposite_trend += [adate]
                                if len(opposite_trend) > len(asize)/3:
                                    insights[f'There is a notable level of variability in the frequency of recorded entries for "{col}" greater than zero. This variability is characterized by alternating increases and decreases in value from one {column_name} to another'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
                                elif len(opposite_trend) == 0:
                                    insights[f'In general, the overarching trend in the frequency of recorded entries for "{col}" greater than zero indicates a negative growth trajectory, with the majority of {column_name} showcasing a downward movement in values'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
                                else:
                                    insights[f'In general, the overarching trend in the frequency of recorded entries for "{col}" greater than zero indicates a negative growth trajectory, with the majority of {column_name} showcasing an downward movement in values. However, this downward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected increase in value. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name ,'Frequency of recorded entries for {col}', asize.to_dict('records')]
        return insights                    
    
    def generate_insights(self, column_name, prev_insights, insight_count):
        insights = {
            'outliers': self.get_outliers(column_name),
            'associations': self.get_associations(column_name),
            'trends': self.get_trends(column_name),
            'distribution': self.get_distributions(column_name),
            'basic_stats': self.get_basic_stats(column_name),
            'rank': self.get_rank(column_name),
            'graphs' : self.graph_insights(column_name,prev_insights,insight_count)
                                        }        

        
        
        #Make sure that each returned insight is unvisited
        output = {}
        for insight in insights.keys():
            if len(insights[insight]) <= insight_count:
                 output[insight] = insights[insight]
                 new_insights_count = len(insights[insight])
            else:
                new_insights_count = min(insight_count,len(insights[insight]) - len([i for i in insights[insight] if i in prev_insights]))
                        
                current_insights = random.sample([v for v in insights[insight] if v not in prev_insights], new_insights_count)
                
                if new_insights_count >= insight_count:
                    prev_insights.extend(current_insights)
                if new_insights_count < insight_count:
                    if prev_insights != []:
                        current_insights.extend(random.sample([i for i in prev_insights if i in insights[insight]], insight_count - len(current_insights)))
                        prev_insights = [v for v in prev_insights if v not in insights[insight]]
                output[insight] = current_insights
        output =  {k: v for k, v in output.items() if v != [] and v != {}}      
        return jsonify({'insights' : output, 'prev_insights' : prev_insights, 'count' : new_insights_count})
            
        
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
    def create_history (self, column_name, dataset_name, user_id, history):
        document = {
        'column_name' : column_name,
        'dataset_name' : dataset_name,
        'user_id' : user_id,
        'history' : history
        }
        query = {'column_name': column_name, 'dataset_name' : dataset_name, 'user_id': user_id}
        if db['hypothesis_history'].find_one(query) is None:
            db['hypothesis_history'].insert_one(document)
        else:
            update_operation = {'$set': {'history': history}}
            db['hypothesis_history'].update_one(query, update_operation)


    def get_hypothesis(self):
        # Get all variables
        column_name = request.json.get('column_name')
        dataset_name = request.json.get('dataset_name')
        user_id = request.json.get('user_id')
        insights = request.json.get('insights')
        context = request.json.get('context')
        data = []
        insights_used = []

        if isinstance(insights, dict):
            insights = [value for list_value in insights.values() for value in list_value]

        # select any two random insights
        if len(insights) >= 2:
            insights = random.sample(insights, 2)
        
        # HuggingFace credentials
        API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
        headers = {"Authorization": "Bearer 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"}
        
        def query_ai(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        
        # get history variable if it exists, else make new history
        query = {'column_name': column_name, 'dataset_name' : dataset_name, 'user_id': user_id}
        if db['hypothesis_history'].find_one(query) is not None:
            history = db['hypothesis_history'].find_one(query)['history']
        else : 
            history = []

        # check if context is not empty
        if context and context != ".":
            # make API call to generate hypothesis with the context
            output = query_ai({
                "inputs": "User Inputs: " + str(history) + "\nCurrent Input: " + context + "\nGenerate an answer for why this is the case in the form of a hypothesis. Make sure to reference the current input in the hypothesis." + "\nAnswer:",
                "parameters": {
                    "return_full_text": False,
                    "repetition_penalty": 1.5,
                    "temperature": 0.6,
                    "max_time": 1.5
                    }
            })
            # insert context to history
            history.insert(0, context)
            if len(history) > 100:
                history.pop()
            try:
                # add output to dictionary
                data.append(output[0]['generated_text'])
                insights_used.append(context)
            except KeyError as e:
                pass
        
        # look at first 2 insights
        for insight in insights:
            # generate hypothesis with insights
            output = query_ai({
                "inputs": "User Inputs: " + str(history) + "\nCurrent Input: " + insight + "\nGenerate an answer for why this is the case in the form of a hypothesis. Make sure to reference the current input in the hypothesis." + "\nAnswer:",
                "parameters": {
                    "return_full_text": False,
                    "repetition_penalty": 1.5,
                    "temperature": 0.6,
                    "max_time": 1.5
                    }
            })
            history.insert(0, insight)
            if len(history) > 10:
                history.pop()
            try:
                data.append(output[0]['generated_text'])
                insights_used.append(insight)
            except KeyError as e:
                pass
        
        # create/update history variable
        self.create_history (column_name, dataset_name, user_id, history)
        
        return jsonify({'data' : data,
                        'insights_used': insights_used})
