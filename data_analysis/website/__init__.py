from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1a50323c4d851acc618685b37c14439bca33d8ea1275d688cbabf07973621814'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import Athlete, Record
    
    if not path.exists('website/database.db'):
        with app.app_context():
            db.create_all()
     
    return app