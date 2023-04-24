from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import config
from .celery.init import celery_init_app

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name):
    """Create an instance of this flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_prefixed_env('POETPIECE')

    with app.app_context():
        from . import errors

    # Initialize Flask extensions
    db.init_app(app)
    celery_init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .main import main as main_bp
    app.register_blueprint(main_bp)

    from .poems import poems as poems_bp
    app.register_blueprint(poems_bp)

    from .resources import resources as resources_bp
    app.register_blueprint(resources_bp)
    
    return app
