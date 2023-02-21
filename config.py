import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Contain base configuration settings for this application."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_POEMS_PER_PAGE = 6
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Inherit from Config and provide custom configurations for dev mode."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "application-dev.sqlite")}'


class TestingConfig(Config):
    """Add custom configurations to Config for test mode."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    """Contain extra configurations for production environment."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "application.sqlite")}'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    'default': DevelopmentConfig
}
