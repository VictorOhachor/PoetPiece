from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_caching import Cache
from config import config
from flask_migrate import Migrate
from flask_mail import Mail
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()
mail = Mail()
migrate = Migrate(db=db)

def create_app(config_name):
    """Create an instance of this flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_prefixed_env('POETPIECE')

    with app.app_context():
        from .helpers import cleanup
        from . import errors

    # Initialize Flask extensions
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    migrate.init_app(app)

    # Initialize Sentry
    sentry_sdk.init(
        dsn="https://9ca092c424c9c6a4e245e08050c62c4e@o4505762974859264.ingest.sentry.io/4505763024142336",
        integrations=[
            FlaskIntegration(),
        ],

        traces_sample_rate=.6
    )

    # Register blueprints
    from .main import main as main_bp
    app.register_blueprint(main_bp)

    from .poems import poems as poems_bp
    app.register_blueprint(poems_bp)

    from .resources import resources as resources_bp
    app.register_blueprint(resources_bp)

    # Set the login page for the login manager
    login_manager.login_view = 'main.login'
    
    return app
