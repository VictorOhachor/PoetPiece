import os
from app import create_app, db
from app.models import User, Admin, Poem, Category, Stanza, Comment
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.context_processor



@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Admin': Admin,
        'Poem': Poem, 'Category': Category,
        'Stanza': Stanza, 'Comment': Comment
    }


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
