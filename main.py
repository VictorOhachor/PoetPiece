import os
from app import create_app, db
from app.models import (User, Poet, Poem, Category, Stanza, Comment,
                        Notification)
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

# make celery app available globally.
celery_app = app.extensions['celery']


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Poet': Poet,
        'Poem': Poem, 'Category': Category,
        'Stanza': Stanza, 'Comment': Comment,
        'Notification': Notification
    }


@app.context_processor
def inject_data():
    return {
        'unread_notifs': Notification.count_unread(),
    }


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
