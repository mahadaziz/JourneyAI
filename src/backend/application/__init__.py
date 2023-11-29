from flask import Flask
from flask_cors import CORS,cross_origin
from  pymongo.mongo_client import MongoClient 

from dotenv import load_dotenv
import os 



load_dotenv()

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")


# Session config


mongodb_client = MongoClient(app.config['MONGO_URI'])

app.secret_key = os.getenv("SECRET_KEY")

# Initialize the database and store it in a db variable

db = mongodb_client.db

from application import routes, models
