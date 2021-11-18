import os

from flask import Flask
from flask_mongoengine import MongoEngine
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

dbhost = os.getenv('MONGO_URI')

app.config['MONGODB_SETTINGS'] = {
    'host': dbhost
}

db = MongoEngine(app)

class UserData(db.Document):
    face = db.StringField(required=True)
    plate = db.StringField(required=True)
    platenumber = db.StringField(required=True)
    checkintime = db.DateField(required=True)
    checkouttime = db.DateField()
    ischeck = db.BooleanField()