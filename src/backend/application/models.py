import os
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
    
    @staticmethod
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

    def __init__(self, rows):
        df = pd.DataFrame(rows).drop(columns=['_id'], errors='ignore')
        df = df.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how='all')
        for col in df.select_dtypes(exclude='number'):
            df[col] = df[col].map(str, na_action='ignore')
        self.data = df
        self.DATE_LIKE_COLUMNS = [col for col in df if self.is_year_or_date_column(df[col], col)]
        remaining = df.drop(columns=self.DATE_LIKE_COLUMNS)
        self.NUMERICAL_COLUMNS = remaining.select_dtypes(include=['int64', 'float64']).columns.tolist()
        self.CATEGORICAL_COLUMNS = remaining.select_dtypes(include=['object', 'category']).columns.tolist()

    def get_outliers(self, column_name):
        df = self.data

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
        df = self.data

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
                    current_counts = df_sorted[df_sorted[column_name] == curr_segment][cat_col].value_counts()
                    next_counts = df_sorted[df_sorted[column_name] == next_segment][cat_col].value_counts()
                    if current_counts.empty or next_counts.empty:
                        continue
                    curr_seg_most = current_counts.idxmax()
                    next_seg_most = next_counts.idxmax()
                    
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

            # Trend Analysis within Date-Like Column Segments
            for date_col in self.DATE_LIKE_COLUMNS:
                df_sorted = df.sort_values(by=date_col)
                segments = df_sorted[date_col].dropna().unique()

                for i in range(len(segments) - 1):
                    curr_segment = segments[i]
                    next_segment = segments[i + 1]
                    
                    curr_seg_val = df_sorted[df_sorted[date_col] == curr_segment][column_name].iloc[0]
                    next_seg_value = df_sorted[df_sorted[date_col] == next_segment][column_name].iloc[0]
                    
                    if pd.isna(curr_seg_val) or pd.isna(next_seg_value):
                        continue

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
        # Trend Analysis for Categorical Columns
        elif column_name in self.CATEGORICAL_COLUMNS:
            for date_col in self.DATE_LIKE_COLUMNS:
                prev_most_freq_category = None
                for current_date, group in df.groupby(date_col):
                    counts = group[column_name].value_counts()
                    if counts.empty:
                        continue
                    most_freq_category = counts.idxmax()

                    if most_freq_category != prev_most_freq_category:
                        if prev_most_freq_category is not None:
                            insights.append(f"For '{date_col}' period starting {current_date}, {most_freq_category} is the new most frequent instance of {column_name}, going from {prev_most_freq_category}.")
                        else:
                            insights.append(f"For '{date_col}' period starting {current_date}, {most_freq_category} is the new most frequent instance of {column_name}.")
                        prev_most_freq_category = most_freq_category

        return insights

    # Function to get distributions templates

    def get_distributions(self, column_name):
        df = self.data

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
            elif column_skewness < -0.5:
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
                    elif column_skewness < -0.5:
                        col_min = df.loc[df[column_name] < threshold, col].dropna()
                        for val in col_min.unique():
                            insights.append(f'The value in {col} that could be leading to a negative skew in {column_name} is {val}.')
        return insights

    # Function to get basic stats templates
    def get_basic_stats(self, column_name):
        df = self.data.copy()
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category', 'datetime64']).columns.tolist()
        categorical_columns = [ name for name in  categorical_columns if name != '_id' ]
        numerical_columns = [ name for name in  numerical_columns if name != '_id' ]
        # date_columns = df.select_dtypes(include=['datetime64']).columns
        units = {}
        for column in numerical_columns:
            if df[column].dtype == 'int64' and 1400 <= df[column].min() <= df[column].max() <= 2100 and 'year' in column.lower():
                numerical_columns = [name for name in numerical_columns if name != column]
                categorical_columns.append(column)
                df[column] = df[column].astype(int)
               
                pass
            try:
                tempUnits = column.split('(')[-1]
                if tempUnits[-1] == ')':
                    units[column] = tempUnits[:-1]

            except:
                pass

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
            counts = df[column_name].value_counts()
            if not counts.empty:
                insights.append(f"The most frequent value in {column_name} is {counts.index[0]} ({counts.iloc[0]} records).")
            for numerical_column in numerical_columns:
                if df[[column_name, numerical_column]].dropna().empty:
                    continue
                if numerical_column in units.keys():
                    category = df.loc[df[numerical_column].idxmax()][column_name]
                    insights += [f'The record with maximum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmax()][numerical_column]} {units[numerical_column]}']
                    category = df.loc[df[numerical_column].idxmin()][column_name]
                    insights += [f'The record with minimum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmin()][numerical_column]} {units[numerical_column]}']

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

                    std = df.groupby(column_name)[numerical_column].std().dropna().reset_index()
                    if std.empty:
                        continue
                    category = std.loc[std[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the highest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmax()][numerical_column]:.2f} {units[numerical_column]}']

                    category = std.loc[std[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the lowest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmin()][numerical_column]:.2f} {units[numerical_column]}']
                else:
                    category = df.loc[df[numerical_column].idxmax()][column_name]
                    insights += [f'The record with maximum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmax()][numerical_column]}']

                    category = df.loc[df[numerical_column].idxmin()][column_name]
                    insights += [f'The record with minimum {numerical_column} happens when the {column_name} is {int(category) if isinstance(category, float) else category}, in this case the {numerical_column} is equal to {df.loc[df[numerical_column].idxmin()][numerical_column]}']

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

                    std = df.groupby(column_name)[numerical_column].std().dropna().reset_index()
                    if std.empty:
                        continue
                    category = std.loc[std[numerical_column].idxmax()][column_name]
                    insights += [f'The {column_name} with the highest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmax()][numerical_column]:.2f}']

                    category = std.loc[std[numerical_column].idxmin()][column_name]
                    insights += [f'The {column_name} with the lowest standard deviation in {numerical_column} is {int(category) if isinstance(category, float) else category}, the standard deviation is {std.loc[std[numerical_column].idxmin()][numerical_column]:.2f}']

        return insights


    # Function to get rank templates
    def get_rank(self, column_name):
        df = self.data

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

                insights.append(f"In column '{column_name}', the values {top_rank_str} rank highest based on '{num_col}'.")
                insights.append(f"In column '{column_name}', the values {bottom_rank_str} rank lowest based on '{num_col}'.")

        elif column_name in self.NUMERICAL_COLUMNS or column_name in self.DATE_LIKE_COLUMNS:
            for cat_col in self.CATEGORICAL_COLUMNS:
                ranked = df.groupby(cat_col)[column_name].mean().sort_values(ascending=False)
                top_ranks = ranked.head(3).index.tolist()
                bottom_ranks = ranked.tail(3).index.tolist()
                bottom_ranks.reverse()
                top_rank_str = ', '.join(f"'{val}'" for val in top_ranks[:min(3, len(ranked))])
                bottom_rank_str = ', '.join(f"'{val}'" for val in bottom_ranks[-min(3, len(ranked)):])

                insights.append(f"Based on the column '{column_name}', the values {top_rank_str} from the column '{cat_col}' rank highest.")
                insights.append(f"Based on the column '{column_name}', the values {bottom_rank_str} from the column '{cat_col}' rank lowest.")

        return insights

    # Function to get associations templates
    def get_associations(self, column_name):
        df = self.data

        insights = []

        if column_name not in df.columns:
            return []

        # Correlation Insights Between Numerical Columns
        if column_name in self.NUMERICAL_COLUMNS:
            for other_col in self.NUMERICAL_COLUMNS:
                if other_col != column_name:
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
                if category_means.dropna().empty:
                    continue
                highest_mean_category = category_means.idxmax()
                lowest_mean_category = category_means.idxmin()
                insights.append(f"There's a notable association between '{column_name}' and '{cat_col}', where '{highest_mean_category}' consistently aligns with higher values and '{lowest_mean_category}' with lower values.")
        
        # Association Insights for a Categorical Column
        elif column_name in self.CATEGORICAL_COLUMNS:
            for num_col in self.NUMERICAL_COLUMNS:
                valid_data = df.dropna(subset=[column_name, num_col])
                category_means = valid_data.groupby(column_name)[num_col].mean()
                if category_means.empty:
                    continue
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
                    if contingency_table.empty:
                        continue
                    top_combination = contingency_table.unstack().idxmax()
                    insights.append(f"Certain combinations of categories from '{column_name}' and '{cat_col}' occur more frequently than others, especially between '{top_combination[0]}' and '{top_combination[1]}'.")

        return insights
    
    # Function to get graphable insights
    def graph_insights(self, column_name, insight_count):
        import random
        insights = {}
        def datetime_numerical_graph_insights (column_name,col):
            df = self.data.loc[self.data[col] != 0, [column_name, col]].dropna().sort_values(column_name)
            if df[column_name].nunique() < 2:
                return
                            
            asum = df.groupby(column_name)[col].sum().reset_index()
            slope, _, _, _, _ = linregress(asum[column_name], asum[col])                
            if np.abs(slope) < 0.05:  
                insights[f'The total "{col}" is relatively constant across most {column_name}'] = ['line',column_name , col, f'Total {col}', asum.to_dict('records')]
            elif slope >= 0.05:
                opposite_trend = []
                changes = []
                for i in range(1, len(asum)):
                    adate, value = asum.loc[i, [column_name, col]]
                    prev_adate, prev_value = asum.loc[i-1, [column_name, col]]
                    change = value - prev_value
                    changes.append((int(adate) if isinstance(adate, float) else adate, change))
                    if value < prev_value:
                        opposite_trend += [int(adate) if isinstance(adate, float) else adate]
                increases = sorted([c for c in changes if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
                decreases = sorted([c for c in changes if c[1] < 0], key=lambda x: x[1])[:3]
                format_change = lambda ch: f"{ch[0]}"
                increases = ', '.join([format_change(inc) for inc in increases])
                decreases = ', '.join([format_change(dec) for dec in decreases])
                if len(opposite_trend) > len(asum)/3:
                    insights[f'There is a notable level of variability in total "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another. The {column_name} with the highest increases are/is {increases} and the {column_name} with the highest decreases are {decreases}.'] = ['line',column_name , col, f'Total {col}', asum.to_dict('records')]
                elif len(opposite_trend) == 0:
                    insights[f'In general, the overarching trend in total "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values'] = ['line',column_name , col, f'Total {col}', asum.to_dict('records')]
                else:
                    insights[f'In general, the overarching trend in total "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values. However, this upward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected dips. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name , col, f'Total {col}', asum.to_dict('records')]
            else:
                opposite_trend = []
                changes = []
                for i in range(1, len(asum)):
                    adate, value = asum.loc[i, [column_name, col]]
                    prev_adate, prev_value = asum.loc[i-1, [column_name, col]]
                    change = value - prev_value
                    changes.append((int(adate) if isinstance(adate, float) else adate, change))
                    if value > prev_value:
                        opposite_trend += [int(adate) if isinstance(adate, float) else adate]
                increases = sorted([c for c in changes if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
                decreases = sorted([c for c in changes if c[1] < 0], key=lambda x: x[1])[:3]
                format_change = lambda ch: f"{ch[0]}"
                increases = ', '.join([format_change(inc) for inc in increases])
                decreases = ', '.join([format_change(dec) for dec in decreases])
                if len(opposite_trend) > len(asum)/3:
                    insights[f'There is a notable level of variability in total "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another. The {column_name} with the highest increases are/is {increases} and the {column_name} with the highest decreases are {decreases}.'] = ['line',column_name , col, f'Total {col}', asum.to_dict('records')]
                elif len(opposite_trend) == 0:
                    insights[f'In general, the overarching trend in total "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing a downward movement in values'] = ['line',column_name ,f'Total {col}', asum.to_dict('records')]
                else:
                    insights[f'In general, the overarching trend in total "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing an downward movement in values. However, this downward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected increase in value. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name , col, f'Total {col}', asum.to_dict('records')]
            
            
            aavg = df.groupby(column_name)[col].mean().reset_index()
            slope, _, _, _, _ = linregress(aavg[column_name], aavg[col])                
            if np.abs(slope) < 0.05:  
                insights[f'The average "{col}" is relatively constant across most {column_name}'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
            elif slope >= 0.05:
                opposite_trend = []
                changes = []
                for i in range(1, len(aavg)):
                    adate, value = aavg.loc[i, [column_name, col]]
                    prev_adate, prev_value = aavg.loc[i-1, [column_name, col]]
                    change = value - prev_value
                    changes.append((int(adate) if isinstance(adate, float) else adate, change))
                    if value < prev_value:
                        opposite_trend += [int(adate) if isinstance(adate, float) else adate]
                increases = sorted([c for c in changes if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
                decreases = sorted([c for c in changes if c[1] < 0], key=lambda x: x[1])[:3]
                format_change = lambda ch: f"{ch[0]}"
                increases = ', '.join([format_change(inc) for inc in increases])
                decreases = ', '.join([format_change(dec) for dec in decreases])
                if len(opposite_trend) > len(aavg)/3:
                    insights[f'There is a notable level of variability in average "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another. The {column_name} with the highest increases are/is {increases} and the {column_name} with the highest decreases are {decreases}.'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
                elif len(opposite_trend) == 0:
                    insights[f'In general, the overarching trend in average "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
                else:
                    insights[f'In general, the overarching trend in average "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values. However, this upward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected dips. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
            else:
                opposite_trend = []
                changes = []
                for i in range(1, len(aavg)):
                    adate, value = aavg.loc[i, [column_name, col]]
                    prev_adate, prev_value = aavg.loc[i-1, [column_name, col]]
                    change = value - prev_value
                    changes.append((int(adate) if isinstance(adate, float) else adate, change))
                    if value > prev_value:
                        opposite_trend += [int(adate) if isinstance(adate, float) else adate]
                increases = sorted([c for c in changes if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
                decreases = sorted([c for c in changes if c[1] < 0], key=lambda x: x[1])[:3]
                format_change = lambda ch: f"{ch[0]}"
                increases = ', '.join([format_change(inc) for inc in increases])
                decreases = ', '.join([format_change(dec) for dec in decreases])
                if len(opposite_trend) > len(aavg)/3:
                    insights[f'There is a notable level of variability in average "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another. The {column_name} with the highest increases are/is {increases} and the {column_name} with the highest decreases are {decreases}.'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
                elif len(opposite_trend) == 0:
                    insights[f'In general, the overarching trend in average "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing a downward movement in values'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
                else:
                    insights[f'In general, the overarching trend in average "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing an downward movement in values. However, this downward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected increase in value. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name , col, f'Average {col}', aavg.to_dict('records')]
            
            asize = df.groupby(column_name)[col].size().reset_index()
            slope, _, _, _, _ = linregress(asize[column_name], asize[col])                
            if np.abs(slope) < 0.05:  
                insights[f'The frequency of recorded entries for "{col}" is relatively constant across most {column_name}'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
            elif slope >= 0.05:
                opposite_trend = []
                changes = []
                for i in range(1, len(asize)):
                    adate, value = asize.loc[i, [column_name, col]]
                    prev_adate, prev_value = asize.loc[i-1, [column_name, col]]
                    change = value - prev_value
                    changes.append((int(adate) if isinstance(adate, float) else adate, change))
                    if value < prev_value:
                        opposite_trend += [int(adate) if isinstance(adate, float) else adate]
                increases = sorted([c for c in changes if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
                decreases = sorted([c for c in changes if c[1] < 0], key=lambda x: x[1])[:3]
                format_change = lambda ch: f"{ch[0]}"
                increases = ', '.join([format_change(inc) for inc in increases])
                decreases = ', '.join([format_change(dec) for dec in decreases])
                if len(opposite_trend) > len(asize)/3:
                    insights[f'There is a notable level of variability in the frequency of recorded entries for non-zero "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another. The {column_name} with the highest increases are/is {increases} and the {column_name} with the highest decreases are {decreases}.'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
                elif len(opposite_trend) == 0:
                    insights[f'In general, the overarching trend in frequency of recorded entries for non-zero "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
                else:
                    insights[f'In general, the overarching trend in the frequency of recorded entries for non-zero "{col}" indicates a positive growth trajectory, with the majority of {column_name} showcasing an upward movement in values. However, this upward trend is punctuated by notable exceptions in specific  {column_name} , where we observe unexpected dips. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
            else:
                opposite_trend = []
                changes = []
                for i in range(1, len(asize)):
                    adate, value = asize.loc[i, [column_name, col]]
                    prev_adate, prev_value = asize.loc[i-1, [column_name, col]]
                    change = value - prev_value
                    changes.append((int(adate) if isinstance(adate, float) else adate, change))
                    if value > prev_value:
                        opposite_trend += [int(adate) if isinstance(adate, float) else adate]
                increases = sorted([c for c in changes if c[1] > 0], key=lambda x: x[1], reverse=True)[:3]
                decreases = sorted([c for c in changes if c[1] < 0], key=lambda x: x[1])[:3]
                format_change = lambda ch: f"{ch[0]}"
                increases = ', '.join([format_change(inc) for inc in increases])
                decreases = ', '.join([format_change(dec) for dec in decreases])
                if len(opposite_trend) > len(asize)/3:
                    insights[f'There is a notable level of variability in the frequency of recorded entries for non-zero "{col}". This variability is characterized by alternating increases and decreases in value from one {column_name} to another. The {column_name} with the highest increases are/is {increases} and the {column_name} with the highest decreases are {decreases}.'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
                elif len(opposite_trend) == 0:
                    insights[f'In general, the overarching trend in the frequency of recorded entries for non-zero "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing a downward movement in values'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
                else:
                    insights[f'In general, the overarching trend in the frequency of recorded entries for non-zero "{col}" indicates a negative growth trajectory, with the majority of {column_name} showcasing an downward movement in values. However, this downward trend is punctuated by notable exceptions in specific {column_name}, where we observe unexpected increase in value. Those {column_name} are {", ".join(map(str, opposite_trend))}'] = ['line',column_name , col, f'Frequency of recorded entries for {col}', asize.to_dict('records')]
        
        if column_name in self.DATE_LIKE_COLUMNS:  
            for col in self.NUMERICAL_COLUMNS:
                datetime_numerical_graph_insights (column_name,col)
        if column_name in self.CATEGORICAL_COLUMNS:
            for col in self.NUMERICAL_COLUMNS:
                
                df = self.data.loc[self.data[col] != 0, [column_name, col]].dropna()
                asum = df.groupby(column_name)[col].sum().reset_index().sort_values(by=col, ascending=True)
                med = len(asum) // 2
                if len(asum) > 11:
                    high_cat = ', '.join(asum[column_name].tail(5).tolist())  
                    low_cat = ', '.join(asum[column_name].head(5).tolist())
                    if med % 2 != 0:
                        med_cat = asum.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest total '{col}' are {high_cat}, the categories that have lowest total '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name , col, f'Total {col}', asum.to_dict('records')]
                    else:
                        med_cat = f'{asum.iloc[med-1][column_name]},{asum.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest total '{col}' are {high_cat}, the categories that have lowest total '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name , col, f'Total {col}', asum.to_dict('records')]
                elif len(asum) > 5:
                    high_cat = ', '.join(asum[column_name].tail(2).tolist())  
                    low_cat = ', '.join(asum[column_name].head(2).tolist())
                    if med % 2 != 0:
                        med_cat = asum.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest total '{col}' are {high_cat}, the categories that have lowest total '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name , col, f'Total {col}', asum.to_dict('records')]
                    else:
                        med_cat = f'{asum.iloc[med-1][column_name]},{asum.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest total '{col}' are {high_cat}, the categories that have lowest total '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Total {col}', asum.to_dict('records')]
                elif len(asum) > 2:
                    high_cat = asum[column_name].tail(1)  
                    low_cat = asum[column_name].head(1)
                    if med % 2 != 0:
                        med_cat = asum.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest total '{col}' are {high_cat}, the categories that have lowest total '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Total {col}', asum.to_dict('records')]
                    else:
                        med_cat = f'{asum.iloc[med-1][column_name]},{asum.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest total '{col}' are {high_cat}, the categories that have lowest total '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Total {col}', asum.to_dict('records')]
                else:
                    if len(asum) != 0:
                        all_cats = asum[column_name].tolist()
                        all_values = asum[col].tolist()
                        cat_values = list(zip(all_cats, all_values))
                        cat_values = ', '.join([f"{cat} with a total of {value:.2f}" for cat, value in cat_values])
                        insights[f"There are fewer than three distinct {column_name} categories that correspond to non-zero {col} values. The categories and their corresponding total '{col}' values are: {cat_values}."] = ['bar',column_name ,col, f'Total {col}', asum.to_dict('records')]

                aavg = df.groupby(column_name)[col].mean().reset_index().sort_values(by=col, ascending=True)
                med = len(aavg) // 2
                if len(aavg) > 11:
                    high_cat = ', '.join(aavg[column_name].tail(5).tolist())  
                    low_cat = ', '.join(aavg[column_name].head(5).tolist())
                    if med % 2 != 0:
                        med_cat = aavg.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest average '{col}' are {high_cat}, the categories that have lowest average '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]
                    else:
                        med_cat = f'{aavg.iloc[med-1][column_name]},{aavg.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest average '{col}' are {high_cat}, the categories that have lowest average '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]
                elif len(aavg) > 5:
                    high_cat = ', '.join(aavg[column_name].tail(2).tolist())  
                    low_cat = ', '.join(aavg[column_name].head(2).tolist())
                    if med % 2 != 0:
                        med_cat = aavg.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest average '{col}' are {high_cat}, the categories that have lowest average '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]
                    else:
                        med_cat = f'{aavg.iloc[med-1][column_name]},{aavg.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest average '{col}' are {high_cat}, the categories that have lowest average '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]
                elif len(aavg) > 2:
                    high_cat = aavg[column_name].tail(1)  
                    low_cat = aavg[column_name].head(1)
                    if med % 2 != 0:
                        med_cat = aavg.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest average '{col}' are {high_cat}, the categories that have lowest average '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]
                    else:
                        med_cat = f'{aavg.iloc[med-1][column_name]},{aavg.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest average '{col}' are {high_cat}, the categories that have lowest average '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]
                else:
                    if len(aavg) != 0:
                        all_cats = aavg[column_name].tolist()
                        all_values = aavg[col].tolist()
                        cat_values = list(zip(all_cats, all_values))
                        cat_values = ', '.join([f"{cat} with a average of {value:.2f}" for cat, value in cat_values])
                        insights[f"There are fewer than three distinct {column_name} categories that correspond to non-zero {col} values. The categories and their corresponding average '{col}' values are: {cat_values}."] = ['bar',column_name ,col, f'Average {col}', aavg.to_dict('records')]

                asize = df.groupby(column_name)[col].size().reset_index().sort_values(by=col, ascending=True)
                med = len(asize) // 2
                if len(asize) > 11:
                    high_cat = ', '.join(asize[column_name].tail(5).tolist())  
                    low_cat = ', '.join(asize[column_name].head(5).tolist())
                    if med % 2 != 0:
                        med_cat = asize.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest frequency of recorded entries for '{col}' are {high_cat}, the categories that have lowest frequency of recorded entries for '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]
                    else:
                        med_cat = f'{asize.iloc[med-1][column_name]},{asize.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest frequency of recorded entries for '{col}' are {high_cat}, the categories that have lowest frequency of recorded entries for '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]
                elif len(asize) > 5:
                    high_cat = ', '.join(asize[column_name].tail(2).tolist())  
                    low_cat = ', '.join(asize[column_name].head(2).tolist())
                    if med % 2 != 0:
                        med_cat = asize.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest frequency of recorded entries for '{col}' are {high_cat}, the categories that have lowest frequency of recorded entries for '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]
                    else:
                        med_cat = f'{asize.iloc[med-1][column_name]},{asize.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest frequency of recorded entries for '{col}' are {high_cat}, the categories that have lowest frequency of recorded entries for '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]
                elif len(asize) > 2:
                    high_cat = asize[column_name].tail(1)  
                    low_cat = asize[column_name].head(1)
                    if med % 2 != 0:
                        med_cat = asize.iloc[med][column_name]
                        insights[f"The categories of '{column_name}' that have the highest frequency of recorded entries for '{col}' are {high_cat}, the categories that have lowest frequency of recorded entries for '{col}' are {low_cat} and the category that represents the median is '{med_cat}'"] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]
                    else:
                        med_cat = f'{asize.iloc[med-1][column_name]},{asize.iloc[med][column_name]}'
                        insights[f"The categories of '{column_name}' that have the highest frequency of recorded entries for '{col}' are {high_cat}, the categories that have lowest frequency of recorded entries for '{col}' are {low_cat} and the categories that represent the median are '{med_cat}'"] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]
                else:
                    if len(asize) != 0:
                        all_cats = asize[column_name].tolist()
                        all_values = asize[col].tolist()
                        cat_values = list(zip(all_cats, all_values))
                        cat_values = ', '.join([f"{cat} with a frequency of recorded entries for of {value:.2f}" for cat, value in cat_values])
                        insights[f"There are fewer than three distinct {column_name} categories that correspond to non-zero {col} values. The categories and their corresponding frequency of recorded entries for '{col}' values are: {cat_values}."] = ['bar',column_name ,col, f'Frequency of recorded entries forge {col}', asize.to_dict('records')]

        if column_name in self.NUMERICAL_COLUMNS:
            for col in self.DATE_LIKE_COLUMNS:
                datetime_numerical_graph_insights (col,column_name)
            for col in self.NUMERICAL_COLUMNS:
                if col != column_name:
                    pair = self.data[[column_name, col]].dropna()
                    nonzero = pair[(pair != 0).all(axis=1)]

                    def add_scatter(points, x_label, y_label):
                        if points[column_name].nunique() < 2 or points[col].nunique() < 2:
                            return
                        correlation = points[column_name].corr(points[col])
                        slope, intercept, *_ = linregress(points[column_name], points[col])
                        q1, q3 = points.quantile(0.25), points.quantile(0.75)
                        spread = 1.5 * (q3 - q1)
                        outliers = points[((points < q1 - spread) | (points > q3 + spread)).any(axis=1)]
                        expected = slope * outliers[column_name] + intercept
                        above = int((outliers[col] > expected).sum())
                        below = int((outliers[col] < expected).sum())
                        description = f"The correlation between {x_label} and {y_label} is {correlation:.2f}."
                        if above or below:
                            description += f" Of the outliers, {above} fall above the fitted line and {below} below."
                        insights[description] = [
                            'scatter', column_name, col, x_label, y_label, points.to_dict('records'),
                        ]

                    add_scatter(nonzero, f'Non-Zero {column_name}', f'Non-Zero {col}')
                    for datecol in self.DATE_LIKE_COLUMNS:
                        values = self.data[[datecol, column_name, col]].dropna()
                        grouped = values.groupby(datecol)[[column_name, col]]
                        counts = values[[column_name, col]].ne(0).groupby(values[datecol]).sum()
                        for label, points in [('Sum', grouped.sum()), ('Average', grouped.mean()),
                                              ('Frequency of recorded entries', counts)]:
                            add_scatter(points, f'{label} of {column_name} over {datecol}',
                                        f'{label} of {col} over {datecol}')

        return dict(random.sample(list(insights.items()), min(insight_count, len(insights))))                
    
    def generate_insights(self, column_name, prev_insights, insight_count):
        insights = {
            'outliers': self.get_outliers(column_name),
            'associations': self.get_associations(column_name),
            'trends': self.get_trends(column_name),
            'distribution': self.get_distributions(column_name),
            'basic_stats': self.get_basic_stats(column_name),
            'rank': self.get_rank(column_name),
            'graphs' : self.graph_insights(column_name,insight_count)
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
            
def generate_hypothesis(groq_key, hf_token, finding, history):
    instruction = (
        "Suggest one concise, testable hypothesis for a journalist investigating the current "
        "finding. Refer to the finding and present your explanation as a possibility."
    )
    prompt = json.dumps({"recent_inputs": history, "current_finding": finding}, ensure_ascii=False)
    custom_url = os.getenv("HF_INFERENCE_URL") if not groq_key else None
    if custom_url:
        url = custom_url
        payload = {
            "inputs": f"{instruction}\n{prompt}\nHypothesis:",
            "parameters": {"return_full_text": False, "max_new_tokens": 160},
        }
    else:
        if groq_key:
            url = "https://api.groq.com/openai/v1/chat/completions"
            model = "openai/gpt-oss-20b"
        else:
            url = "https://router.huggingface.co/v1/chat/completions"
            model = os.getenv("HF_MODEL") or "Qwen/Qwen3-30B-A3B-Instruct-2507"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt},
            ],
        }
        if groq_key:
            payload.update(max_completion_tokens=512, reasoning_effort="low")
        else:
            payload["max_tokens"] = 160
    response = requests.post(
        url, headers={"Authorization": f"Bearer {groq_key or hf_token}"},
        json=payload, timeout=(5, 30), allow_redirects=False,
    )
    response.raise_for_status()
    result = response.json()
    text = result[0]["generated_text"] if custom_url else result["choices"][0]["message"]["content"]
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Empty hypothesis")
    return text.strip()


class hypothesis:
    def get_hypothesis(self):
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        hf_token = os.getenv("HF_TOKEN", "").strip()
        if not (groq_key or hf_token):
            return jsonify(error="Hypothesis generation is not configured."), 503

        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="Expected a JSON object."), 400
        ticket = body.get("hypothesis_ticket")
        if not isinstance(ticket, str) or not ticket:
            return jsonify(error="Sign in and retry generating hypotheses."), 401
        issued = db.hypothesis_tickets.find_one_and_delete({
            "_id": ticket, "expires_at": {"$gt": datetime.datetime.utcnow()},
        })
        if not issued:
            return jsonify(error="Sign in and retry generating hypotheses."), 401
        scope = {key: issued[key] for key in ("column_name", "dataset_name", "user_id", "dataset_id")}

        context = body.get("context") or ""
        selected = body.get("selected_insights") or []
        if not isinstance(context, str) or not isinstance(selected, list):
            return jsonify(error="Invalid draft or selected insights."), 400
        if not selected:
            insights = body.get("insights") or []
            if isinstance(insights, dict):
                # Graph descriptions are the keys of the graphs group.
                insights = [item for group in insights.values() if isinstance(group, (list, dict))
                            for item in group]
            if not isinstance(insights, list):
                return jsonify(error="Invalid insights."), 400
            selected = random.sample(insights, min(2, len(insights)))
        if any(not isinstance(item, str) for item in selected):
            return jsonify(error="Expected text for each insight."), 400

        inputs = []
        if context.strip() and context.strip() != ".":
            inputs.append(("context_used", context))
        inputs.extend(("insight_used", item) for item in selected if item.strip())
        if not inputs:
            return jsonify(error="Select a finding or write a sentence to generate a hypothesis."), 400

        previous = db.hypothesis_history.find_one(scope)
        history = previous["history"][:10] if previous else []
        logs = []
        for field, finding in inputs:
            try:
                text = generate_hypothesis(groq_key, hf_token, finding, history)
            except requests.HTTPError as exc:
                messages = {
                    401: "The model provider rejected the backend API key.",
                    403: "Check the backend key's inference permissions and access to the selected model.",
                    402: "Inference credits are unavailable for this account.",
                    429: "The model's request limit was reached. Try again later.",
                    503: "The model service is starting or busy. Try again shortly.",
                }
                return jsonify(error=messages.get(exc.response.status_code, "The model provider could not generate a hypothesis.")), 502
            except requests.Timeout:
                return jsonify(error="The model took too long to respond. Try again."), 504
            except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
                return jsonify(error="The model service did not return a usable hypothesis."), 502
            logs.append({
                **scope, "_id": str(uuid.uuid4()), "hypothesis": text,
                "context_used": None, "insight_used": None, field: finding,
                "Thumbs_Up": False, "Thumbs_Down": False,
                "date_created": datetime.datetime.utcnow(),
            })
            history = [finding, *history[:9]]

        db.Hypothesis_logs.insert_many(logs)
        used = [finding for _, finding in inputs]
        db.hypothesis_history.update_one(scope, {"$push": {"history": {
            "$each": list(reversed(used)), "$position": 0, "$slice": 10,
        }}}, upsert=True)
        return jsonify(data=[log["hypothesis"] for log in logs], insights_used=used,
                       hypothesis_ids={log["hypothesis"]: log["_id"] for log in logs})
