import os

basedir = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Contain base configuration settings for this application."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_POEMS_PER_PAGE = int(os.environ.get('FLASK_POEMS_PER_PAGE', 9))
    MAXIMUM_POET_COUNT = int(os.environ.get('MAXIMUM_POET_COUNT', 10))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    CACHE_TYPE = 'simple'
    MAX_CONTENT_LENGTH = 1024 * 1024

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Inherit from Config and provide custom configurations for dev mode."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "application-dev.sqlite")}'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = os.environ.get('MAIL_PORT', '80')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'admin')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'admin')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)


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
