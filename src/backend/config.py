from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY')
    MONGODB_SETTINGS = {
        'host': config('MONGO_URI'),
    }
    
# (config())