import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

# create app instance
app = Flask(__name__)

# app configurations
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'sqlite:///{os.path.join(basedir, "application.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['FLASK_POEMS_PER_PAGE'] = 12

# initialize database object on app
db = SQLAlchemy(app)
# initialize flask-migrate
migrate = Migrate(app, db)

# initialize login manager
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'
# initialize bootstrap extension on app
bootstrap = Bootstrap(app)

from app import views, models