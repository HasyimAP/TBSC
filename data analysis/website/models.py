from . import db

class Athlete(db.Model):
    athlete_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    yob = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String, nullable=False)
    club = db.Column(db.String)
    province = db.Column(db.String)
    
class Record(db.Model):
    rec_id = db.Column(db.Integer, primary_key=True, nullable=False)
    athlete_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    sex = db.Column(db.String, nullable=False)
    yob = db.Column(db.Integer, nullable=False)
    event = db.Column(db.String, nullable=False)
    record = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    competition = db.Column(db.String)
    