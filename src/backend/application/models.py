from flask import Flask, jsonify, request, session, redirect
from application import db
import bcrypt, datetime, uuid, json, random
import pandas as pd
import requests
from scipy.stats import zscore, skew, stats
from sklearn.cluster import KMeans
import numpy as np

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
    DATE_LIKE_COLUMNS = []

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

        insights = []
        if column_name in self.NUMERICAL_COLUMNS:
            # Filter out null values from the column for outlier detection
            non_null_data = df[column_name].dropna()

            Q1 = non_null_data.quantile(0.25)
            Q3 = non_null_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Detect outliers excluding the rows with null values in the specified column
            outliers = df[(df[column_name] < lower_bound) | (df[column_name] > upper_bound)]
            total_outliers = len(outliers)

            # Calculate the percentage of outliers in the column
            percentage_of_outliers = (total_outliers / len(non_null_data)) * 100

            if total_outliers > 0:
                insights.append(f'Found {total_outliers} outliers in {column_name}, constituting {percentage_of_outliers:.2f}% of the data.')

                # Analyze relationships with combined categorical columns
                for col in combined_categorical_columns:
                    common_values = outliers[col].value_counts()
                    if not common_values.empty:
                        most_common = common_values.idxmax()
                        percentage_in_outliers = (common_values.max() / total_outliers) * 100
                        insights.append(f'{most_common} is the {col} with the most outliers in {column_name} at {percentage_in_outliers:.2f}% of the outliers.')
        return insights

    # Function to get trends templates

    def get_trends(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []

        # Check if column exists
        if column_name not in df.columns:
            return []

        # Trend Analysis for Numerical Columns
        if column_name in self.NUMERICAL_COLUMNS:
            df['z_scores'] = zscore(df[column_name].fillna(0))
            overall_trend_direction = "upward" if df[column_name].iloc[-1] > df[column_name].iloc[0] else "downward"

            # Analyze parallel and inverse trends with other numerical columns
            for other_col in self.NUMERICAL_COLUMNS:
                if other_col != column_name:
                    other_col_trend = "upward" if df[other_col].iloc[-1] > df[other_col].iloc[0] else "downward"
                    trend_relation = "parallel" if overall_trend_direction == other_col_trend else "inverse"
                    insights.append(f"Overall, '{column_name}' and '{other_col}' have a {trend_relation} trend.")

            insights.append(f"Overall, '{column_name}' shows a {overall_trend_direction} trend.")

            # Trend Analysis within Date-Like Column Segments
            for date_col in self.DATE_LIKE_COLUMNS:
                df_sorted = df.sort_values(by=date_col)
                segments = df_sorted[date_col].dropna().unique()

                for segment in segments:
                    segment_data = df_sorted[df_sorted[date_col] == segment]
                    segment_trend = "upward" if segment_data[column_name].iloc[-1] > segment_data[column_name].iloc[0] else "downward"
                    insights.append(f"In the period around {segment}, '{column_name}' shows a {segment_trend} trend.")

                    # Analyzing trend relation within segments
                    for other_col in self.NUMERICAL_COLUMNS:
                        if other_col != column_name:
                            other_segment_data = df_sorted[df_sorted[date_col] == segment]
                            other_segment_trend = "upward" if other_segment_data[other_col].iloc[-1] > other_segment_data[other_col].iloc[0] else "downward"
                            trend_relation = "parallel" if segment_trend == other_segment_trend else "inverse"
                            insights.append(f"In the period around {segment}, '{column_name}' and '{other_col}' have a {trend_relation} trend.")

        # Trend Analysis for Categorical Columns
        elif column_name in self.CATEGORICAL_COLUMNS and self.DATE_LIKE_COLUMNS:
            for date_col in self.DATE_LIKE_COLUMNS:
                grouped_data = df.groupby([date_col, column_name]).size().reset_index(name='count')
                sorted_grouped_data = grouped_data.sort_values(by=date_col)

                prev_most_freq_category = None
                for _, group in sorted_grouped_data.groupby(date_col):
                    current_date = group[date_col].iloc[0]
                    most_freq_category = group.loc[group['count'].idxmax()][column_name]

                    if most_freq_category != prev_most_freq_category:
                        insights.append(f"For '{date_col}' period starting {current_date}, '{column_name}' shows a trend towards category '{most_freq_category}'.")
                        prev_most_freq_category = most_freq_category

        return insights

    # Function to get distributions templates

    def get_distributions(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []

        if column_name not in df.columns:
            return []

        non_null_data = df[column_name].dropna()

        if column_name in self.NUMERICAL_COLUMNS:
            column_skewness = skew(non_null_data)
            skew_type = "positively" if column_skewness > 0 else "negatively"
            general_skew_type = "right-skewed" if column_skewness > 0 else "left-skewed" if column_skewness < 0 else "symmetric"
            skew_description = "few unusually high" if skew_type == "positively" else "few unusually low"

            # General insight about the skewness of the column
            insights.append(f"Overall, '{column_name}' is generally {general_skew_type}, indicating {skew_description} values.")

            # Determine skewed instances
            threshold = non_null_data.mean() + 2 * non_null_data.std() if skew_type == "positively" else non_null_data.mean() - 2 * non_null_data.std()
            skewed_instances = df[(df[column_name] > threshold) if skew_type == "positively" else (df[column_name] < threshold)]

            if skewed_instances.empty:
                return insights  # Returns the general insight if no skewed instances are found

            representative_value = skewed_instances[column_name].iloc[0]  # Example representative value

            # Analyze each other column
            for col in df.columns:
                if col != column_name:
                    if not skewed_instances[col].mode().empty:
                        most_common_value = skewed_instances[col].mode()[0]
                        category_percentage = skewed_instances[col].value_counts()[most_common_value] / len(skewed_instances) * 100
                        insights.append(f"With '{column_name}' being {skew_type} skewed, there are {skew_description} values, with an instance being {representative_value}. In '{col}', the most common corresponding value is '{most_common_value}' at {category_percentage:.2f}% of these instances.")
                    else:
                        insights.append(f"With '{column_name}' being {skew_type} skewed, '{col}' does not show a clear mode in the skewed instances.")

        return insights

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
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))
        if column_name not in self.NUMERICAL_COLUMNS:
            return []

        # Remove NaN values from the column
        clean_df = df.dropna(subset=[column_name])

        # Determine the optimal number of clusters using the Elbow Method
        optimal_k = self.find_optimal_clusters(clean_df[[column_name]])
        if optimal_k is None:
            return []

        # Perform clustering with the optimal number of clusters
        kmeans = KMeans(n_clusters=optimal_k)
        kmeans.fit(clean_df[[column_name]])
        clean_df['cluster'] = kmeans.labels_

        # Generate insights
        insights = self.generate_cluster_insights(clean_df, column_name, optimal_k)

        return insights

    def find_optimal_clusters(self, data):
        distortions = []
        K = range(1, 10)  # Testing 1 to 9 clusters
        for k in K:
            kmeanModel = KMeans(n_clusters=k)
            kmeanModel.fit(data)
            distortions.append(kmeanModel.inertia_)

        # Find the elbow point
        k_distances = np.diff(distortions)
        second_derivative = np.diff(k_distances)
        elbow_point = np.argmax(second_derivative) + 2  # +2 due to double differencing
        if elbow_point > 0 and elbow_point < len(K):
            return elbow_point
        return None
    
    def generate_cluster_insights(self, df, column_name, num_clusters):
        insights = []

        # Characteristics of Clusters in the Chosen Column
        for cluster in sorted(df['cluster'].unique()):
            cluster_mean = df[df['cluster'] == cluster][column_name].mean()
            insights.append(f'{num_clusters} clusters found in {column_name}. Cluster {cluster} has an average value of {cluster_mean:.2f}.')

        # Correlation with Other Numerical Columns
        for other_col in self.NUMERICAL_COLUMNS:
            if other_col != column_name:
                for cluster in sorted(df['cluster'].unique()):
                    cluster_mean = df[df['cluster'] == cluster][column_name].mean()
                    mean_value = df[df['cluster'] == cluster][other_col].mean()
                    insights.append(f'Cluster {cluster} (avg {column_name}: {cluster_mean:.2f}) correlates with an average {other_col} value of {mean_value:.2f}')

        # Interaction with Categorical Columns
        for cat_col in self.CATEGORICAL_COLUMNS:
            for cluster in sorted(df['cluster'].unique()):
                cluster_mean = df[df['cluster'] == cluster][column_name].mean()
                most_common_category = df[df['cluster'] == cluster][cat_col].mode()[0]
                insights.append(f'In Cluster {cluster} (avg {column_name}: {cluster_mean:.2f}), the most common category in {cat_col} is {most_common_category}')

        # Insights on Outliers Within Clusters
        for cluster in sorted(df['cluster'].unique()):
            cluster_data = df[df['cluster'] == cluster][column_name]
            cluster_mean = cluster_data.mean()
            std_dev = cluster_data.std()
            lower_bound = cluster_mean - 2 * std_dev
            upper_bound = cluster_mean + 2 * std_dev
            outliers = df[(df['cluster'] == cluster) & ((df[column_name] < lower_bound) | (df[column_name] > upper_bound))]
            insights.append(f'Cluster {cluster} (avg {column_name}: {cluster_mean:.2f}) has {len(outliers)} outliers. This might indicate special cases or anomalies within this group.')

        return insights

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

    # Function to get derived values templates
    def get_derived_values(self, column_name):
        return [
            f'Derived values from {column_name} provide additional insights. For instance, consider the derived value {column_name} = {round(random.uniform(40, 50),2)}.',
            f'{column_name} derived values contribute to the overall analysis. A notable derived value is {column_name} = {round(random.uniform(60, 70),2)}.',
            f'Incorporating derived values enhances the understanding of {column_name}. Explore insights from values like {column_name} = {round(random.uniform(70, 80),2)}.'
        ]

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
                insights.append(f"Analysis shows that different categories in '{column_name}' have significantly different average values in '{num_col}', particularly '{top_category}' with the highest average.")

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

    # Function to get differences templates
    def get_differences(self, column_name):
        cursor = db['cars'].find()
        df = pd.DataFrame(iter(cursor))

        insights = []
        if column_name in df.columns and df[column_name].dtype in ['int64', 'float64']:
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns

        
            # 2. Differences in Relation to Categorical Columns
            for cat_column in categorical_columns:
                if cat_column != column_name:
                    grouped_diff = df.groupby(cat_column)[column_name].mean()
                    #insights.append(f'Differences in {column_name} are observed when grouped by {cat_column}. Average values per group: {grouped_diff.to_dict()}.')

            # 3. Specific Examples
            for cat_column in categorical_columns:
                if cat_column != column_name:
                    sample_groups = df.groupby(cat_column).apply(lambda x: x.sample(1)).reset_index(drop=True).head(3)
                    for _, row in sample_groups.iterrows():
                        example_insight = f'For example, in the {cat_column} group "{row[cat_column]}", the value of {column_name} is {row[column_name]:.2f}.'
                        #insights.append(example_insight)

        return insights
    
    def generate_insights(self, column_name, prev_insights, insight_count):
        insights = {
             'outliers' : self.get_outliers(column_name),
            # 'derived values' : self.get_derived_values(column_name),
             'associations' : self.get_associations(column_name),
            # 'differences' : self.get_differences(column_name),
             'trends' : self.get_trends(column_name),
             'distribution' : self.get_distributions(column_name),
             'basic_stats' : self.get_basic_stats(column_name),
             'clusters' : self.get_clusters(column_name),
             'rank' : self.get_rank(column_name)
                                        }        

        
        
        #Make sure that each returned insight is unvisited
        output = {}
        for insight in insights.keys():
            if len(insights[insight]) <= insight_count:
                 output[insight] = insights[insight]
            else:
                new_insights_count = min(insight_count,len(insights[insight]) - len([i for i in insights[insight] if i in prev_insights]))
                        
                current_insights = random.sample([v for v in insights[insight] if v not in prev_insights], new_insights_count)
                
                if new_insights_count >= insight_count:
                    prev_insights.extend(current_insights)
                if new_insights_count < insight_count:
                    print (current_insights)
                    if prev_insights != []:
                        current_insights.extend(random.sample([i for i in prev_insights if i in insights[insight]], insight_count - len(current_insights)))
                        prev_insights = [v for v in prev_insights if v not in insights[insight]]
                output[insight] = current_insights
                
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
                    "max_time": 2.0,
                    "temperature": 0.5,
                    "repetition_penalty": 1.03
                    }
            })
            # insert context to history
            history.insert(0, context)
            if len(history) > 100:
                history.pop()
            try:
                # add output to dictionary
                data.append(output[0]['generated_text'])
            except KeyError as e:
                pass
        
        # look at first 2 insights
        for insight in insights[:2]:
            # generate hypothesis with insights
            output = query_ai({
                "inputs": "User Inputs: " + str(history) + "\nCurrent Input: " + insight + "\nGenerate an answer for why this is the case in the form of a hypothesis. Make sure to reference the current input in the hypothesis." + "\nAnswer:",
                "parameters": {
                    "return_full_text": False,
                    "max_time": 2.0,
                    "temperature": 0.5,
                    "repetition_penalty": 1.03
                    }
            })
            history.insert(0, insight)
            if len(history) > 100:
                history.pop()
            try:
                data.append(output[0]['generated_text'])
            except KeyError as e:
                pass
        
        # create/update history variable
        self.create_history (column_name, dataset_name, user_id, history)
        
        return jsonify({'data' : data})
