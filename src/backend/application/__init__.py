from flask import Flask
from flask_cors import CORS,cross_origin
from  pymongo.mongo_client import MongoClient 
from flask_session import Session

from dotenv import load_dotenv
import os 



load_dotenv()

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = os.getenv("SECRET_KEY")

# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")


# Session config
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session_'

app.config['SESSION_MONGODB_DB'] = 'Sessions'

# Initialize the database and store it in a db variable

mongodb_client = MongoClient(app.config['MONGO_URI'])
db = mongodb_client.db

app.config['SESSION_MONGODB'] = mongodb_client

Session(app)
from application import routes, models
