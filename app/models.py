from . import db, login_manager
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func
from uuid import uuid4


class BaseModel(db.Model):
    """Serves as the base for every model in this application."""

    __abstract__ = True

    def _id():
        """Generate a uuid and return the 32-char string."""
        return uuid4().hex

    id = db.Column(db.String(255), primary_key=True, default=_id)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def save(self):
        """Save instance to database."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def create(cls, **kwargs):
        """Create a new record in the table."""
        record = cls(**kwargs)
        record.save()

    def delete(self):
        """Remove instance from database."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """String representation of a model's instance."""
        return f'[{type(self).__name__} {self.id}] -- Created on {self.created_at}'

    def to_dict(self):
        ins_d = {}

        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                ins_d[key] = value

        return ins_d

    @classmethod
    def find_all(cls):
        """Fetch all stanza from the database."""
        return cls.query.all()

    @classmethod
    def find_by(cls, **kwargs):
        """Fetch records from db based on fields passed."""
        fetch_one = kwargs.pop('one', False)
        query = cls.query.filter_by(**kwargs)

        if fetch_one:
            return query.first()
        return query.all()

    @classmethod
    def find_order_by(cls, *args, **kwargs):
        """Fetch records from db by kwargs and order them by args passed."""
        records = cls.query.filter_by(**kwargs).order_by(*args).all()
        return records

    @classmethod
    def get_choices(cls):
        """Get all records as WTForms select field choices."""
        pass


class User(UserMixin, BaseModel):
    """Model representing a user instance."""

    __tablename__ = 'users'

    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(255))
    birth_date = db.Column(db.Date)

    # foreign keys
    poet = db.relationship('Poet', backref='users', uselist=False)
    comments = db.relationship('Comment', backref='users', lazy='dynamic')

    @property
    def last_login(self):
        return self.updated_at

    @property
    def is_poet(self):
        """Check that user is an poet."""
        poet_exists = Poet.query.filter_by(user_id=self.id).first()
        return bool(poet_exists)

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

    @classmethod
    def find_by_username(cls, username):
        return cls.find_by(username=username, one=True)


class Poet(BaseModel):
    """Model representing an poet instance."""

    __tablename__ = 'poets'

    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), unique=True)
    email = db.Column(db.String(255), unique=True, index=True)
    gender = db.Column(db.String(10), nullable=False)
    verified = db.Column(db.Boolean, default=False)

    # foreign keys
    poems = db.relationship('Poem', backref='poets', lazy='dynamic')

    @property
    def became_poet_on(self):
        """Return the date that user became a poet."""
        return self.created_at

    @classmethod
    def reached_limit(cls):
        """Limit the number of registered poets that can be verified."""
        poets_count = cls.query.filter_by(verified=True).count()
        max_poets_count = current_app.config['MAXIMUM_POET_COUNT']

        return True if poets_count >= max_poets_count else False

    @classmethod
    def get_choices(cls):
        return [(poet.users.username,
                                 poet.users.username.capitalize())
                                for poet in cls.find_all()]


class Category(BaseModel):
    """Model representing a category instance."""

    __tablename__ = 'categories'

    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000))

    # foreign keys
    poems = db.relationship('Poem', backref='categories', lazy='dynamic')

    @classmethod
    def get_id(cls, name):
        category = cls.query.filter_by(name=name).first()

        if category:
            return category.id

    @classmethod
    def get_choices(cls):
        return [(category.name, category.name.upper())
                for category in cls.find_all()]


class Poem(BaseModel):
    """Model representing a poem instance."""

    __tablename__ = 'poems'

    author_id = db.Column(db.String(255), db.ForeignKey('poets.id',
                                                        ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(3000), nullable=True)
    category_id = db.Column(db.String(255), db.ForeignKey('categories.id',
                                                          ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    premium = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=False)

    # foreign keys
    stanzas = db.relationship(
        'Stanza', backref='poems', lazy='dynamic', cascade='all, delete, delete-orphan')
    comments = db.relationship('Comment', backref='poems', lazy='dynamic',
                               cascade='all,delete')

    @property
    def crafted_on(self):
        return self.created_at

    @property
    def is_accessible(self):
        """Check if current user is authorized to view or manipulate poem."""
        if current_user.is_poet:
            poet = Poet.find_by(user_id=current_user.id, one=True)
            if self.author_id == poet.id:
                return True
        return False

    def publish(self):
        """Publish or unpublish a poem."""
        self.published = not self.published
        self.save()

    @classmethod
    def get_choices(cls):
        return [(poem.title, poem.title.upper())
                for poem in cls.find_all()]


class Stanza(BaseModel):
    """Model representing a stanza of a poem."""

    __tablename__ = 'stanzas'

    poem_id = db.Column(db.String(255), db.ForeignKey(
        'poems.id', ondelete='CASCADE'))
    index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    @property
    def added_on(self):
        return self.created_at

    @property
    def edited_on(self):
        return self.updated_at


class Comment(BaseModel):
    """Model representing a comment made by a user on a poem."""

    __tablename__ = 'comments'

    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    poem_id = db.Column(db.String(255), db.ForeignKey(
        'poems.id', ondelete='CASCADE'))
    comment = db.Column(db.String(1000), default='I love this!')
    approved = db.Column(db.Boolean, default=False)

    @property
    def last_edit(self):
        return self.updated_at


class PoemRating(BaseModel):
    """Model representing rating given by a user to a poem."""

    __tablename__ = 'poem_ratings'

    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    poem_id = db.Column(db.String(255), db.ForeignKey(
        'poems.id', ondelete='CASCADE'))
    rating = db.Column(db.Float, default=0.0)

    @property
    def rated_on(self):
        return self.created_at


class Notification(BaseModel):
    """Store notifications that can be accessed by the user."""

    __tablename__ = 'notifications'

    unread = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id', ondelete='SET NULL'), nullable=True)
    content = db.Column(db.String(512), nullable=False)
    in_trash = db.Column(db.Boolean, default=False)
    type_ = db.Column(db.String(32), nullable=False)

    def get_user(self):
        """Get the user's username associated with a notification."""
        user = User.find_by(id=self.user_id, one=True)
        if not user:
            return 'System'
        return user.username

    @classmethod
    def count_unread(cls):
        """Get the count of all unread notifications."""
        unread_notifications = len(cls.find_by(unread=True))
        return unread_notifications


@login_manager.user_loader
def load_user(user_id):
    """Get user data from database."""
    return User.query.get(user_id)
