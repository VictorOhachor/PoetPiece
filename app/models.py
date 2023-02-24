from . import db, login_manager
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func

from .utils import generate_id


class User(UserMixin, db.Model):
    """Model representing a user instance."""

    __tablename__ = 'users'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(255))
    birth_date = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """Restrict read access on plain text password."""
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verify that password is correct."""
        return check_password_hash(self.password_hash, password)

    # foreign keys
    admin = db.relationship('Admin', backref='users', uselist=False)
    comments = db.relationship('Comment', backref='users', lazy='dynamic')

    def __repr__(self):
        """Official string representation of a user object."""
        return f'<{type(self).__name__}: {self.username}>'


class Admin(db.Model):
    """Model representing an admin instance; Inherit from User class."""

    __tablename__ = 'admins'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), unique=True)
    email = db.Column(db.String(255), unique=True, index=True)
    gender = db.Column(db.String(10), nullable=False)
    verified = db.Column(db.Boolean, default=False)

    # foreign keys
    poems = db.relationship('Poem', backref='admin', lazy='dynamic')

    def __repr__(self):
        """Official string representation of an admin object."""
        return f'<{type(self).__name__}: User {self.user_id} ({self.gender})>'

    @staticmethod
    def reached_admin_count():
        """Limit the number of admins that can be registered."""
        admins = Admin.query.all()

        if len(admins) == current_app.config['NUMBER_OF_ADMINS_ALLOWED']:
            return True
        return False


class Category(db.Model):
    """Model representing a category instance."""

    __tablename__ = 'categories'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000), unique=True)

    # foreign keys
    poems = db.relationship('Poem', backref='categories', lazy='dynamic')

    def __repr__(self):
        """Official string representation of a category object."""
        return f'<{type(self).__name__}: {self.name}>'


class Poem(db.Model):
    """Model representing a poem instance."""

    __tablename__ = 'poems'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    author_id = db.Column(db.String(255), db.ForeignKey('admins.id',
                                                   ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.String(255), db.ForeignKey('categories.id',
    ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    premium = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=False)
    crafted_on = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    # foreign keys
    stanzas = db.relationship(
        'Stanza', backref='poems', lazy='dynamic', cascade='all,delete')
    comments = db.relationship('Comment', backref='poems', lazy='dynamic',
    cascade='all,delete')

    def __repr__(self):
        """Official string representation of a poem object."""
        poem_type = 'Premium' if self.premium else 'Free'
        return f'<{type(self).__name__}: {self.title} ({poem_type})>'


class Stanza(db.Model):
    """Model representing a stanza of a poem."""

    __tablename__ = 'stanzas'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    poem_id = db.Column(db.String(255), db.ForeignKey('poems.id', ondelete='CASCADE'))
    index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    added_on = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
    edited_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        """Official string representation of a stanza object."""
        poem = Poem.query.get(self.poem_id)
        poem_title = poem.title if poem else ''
        return f'<{type(self).__name__}: {self.index} (of {poem_title})>'


class Comment(db.Model):
    """Model representing a comment made by a user on a poem."""

    __tablename__ = 'comments'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id', ondelete='CASCADE'))
    poem_id = db.Column(db.String(255), db.ForeignKey('poems.id', ondelete='CASCADE'))
    comment = db.Column(db.String(1000), default='I love this!')
    approved = db.Column(db.Boolean, default=False)
    last_edit = db.Column(db.DateTime, server_default=func.now(),
                          onupdate=func.now())

    def __repr__(self):
        """Official string representation of a comment object."""
        poem = Poem.query.get(self.poem_id)
        user = User.query.get(self.user_id)

        return f'<{type(self).__name__}: {self.id} on {poem.title} by {user.username}>'


class PoemRating(db.Model):
    """Model representing rating given by a user to a poem."""

    __tablename__ = 'poem_ratings'

    id = db.Column(db.String(255), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id', ondelete='CASCADE'))
    poem_id = db.Column(db.String(255), db.ForeignKey('poems.id', ondelete='CASCADE'))
    rating = db.Column(db.Float, default=0.0)
    rated_on = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        """Official string representation of a PoemRating object."""
        poem = Poem.query.get(self.poem_id)
        user = User.query.get(self.user_id)

        return f'<{type(self).__name__}: {self.id} on {poem.title} by {user.username} ({self.rating})'


@login_manager.user_loader
def load_user(user_id):
    """Get user data from database."""
    return User.query.get(user_id)
