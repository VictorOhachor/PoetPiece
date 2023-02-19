from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name):
    """Create an instance of this flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize Flask extensions
    bootstrap.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .poems import poems as poems_blueprint
    app.register_blueprint(poems_blueprint)

    return app
