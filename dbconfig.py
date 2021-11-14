from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host':'mongodb+srv://eliteaddy:adeshile@cluster0-ufp8b.mongodb.net/recognizer?retryWrites=true'
}

db = MongoEngine(app)

class UserData(db.Document):
    face = db.StringField(required=True)
    plate = db.StringField(required=True)
    platenumber = db.StringField(required=True)
    checkintime = db.DateField(required=True)
    checkouttime = db.DateField()
    ischeck = db.BooleanField()