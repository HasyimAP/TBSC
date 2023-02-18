from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from .models import *
from . import db
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/athlete', methods=['GET', 'POST'])
def athlete():
    if request.method == 'POST':
        athlete_id = request.form.get('athlete_id')
        name = request.form.get('name')
        sex = request.form.get('sex')
        yob = request.form.get('yob')
        club = request.form.get('club')
        province = request.form.get('province')

        exist_athlete = Athlete.query.filter_by(athlete_id = athlete_id).all()
        
        if exist_athlete:
            for x in exist_athlete:
                del_athlete = Athlete.query.get(x.athlete_id)
                db.session.delete(del_athlete)
                db.session.commit()
            
        new_athlete = Athlete(athlete_id = athlete_id,
                              name = name.upper(),
                              yob = yob,
                              sex = sex,
                              club = club.upper(),
                              province = province.upper()
                              )
        
        db.session.add(new_athlete)
        db.session.commit()
        
        flash('Athlete successfully updated')
        
    return render_template('athlete.html')

@auth.route('/record', methods=['GET', 'POST'])
def record():
    names = [x.name for x in Athlete.query.all()]
    
    if request.method == 'POST':
        name = request.form.get('name')
        event = request.form.get('event')
        record = request.form.get('record')
        date = request.form.get('date')
        competition = request.form.get('competition')
    
        date = datetime.strptime(date, '%Y-%m-%d')
    
        exist_record = Record.query.filter_by(name = name.upper(), date = date, event = event.upper()).all()
        
        if exist_record:
            for x in exist_record:
                del_record = Record.query.get(x.rec_id)
                db.session.delete(del_record)
                db.session.commit()
    
        athlete_id = Athlete.query.filter_by(name = name).first().athlete_id
        sex = Athlete.query.filter_by(name = name).first().sex
        yob = Athlete.query.filter_by(name = name).first().yob
        
        new_record = Record(name = name,
                            athlete_id = athlete_id,
                            event = event.upper(),
                            record = record,
                            date = date,
                            sex = sex,
                            yob = yob,
                            competition = competition.upper()
                            )
        
        db.session.add(new_record)
        db.session.commit()
    
        flash('Record successfully updated')

    return render_template('record.html',
                           names = names
                           )

# class Athlete_Form(FlaskForm):
#     athlete_id = IntegerField('Athlete ID', validators=[DataRequired])
#     name = StringField('Athlete Full Name', validators=[DataRequired])
#     yob = IntegerField('Year of Birth', validators=[DataRequired])
#     club = StringField('Swimming Club')
#     province = StringField('Province')
    
# class Record_Form(FlaskForm):
#     name = StringField('Athlete Full Name', validators=[DataRequired])
#     event = StringField('Event', validators=[DataRequired])