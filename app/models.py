from . import db, login_manager
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func
from uuid import uuid4
from enum import Enum
from markdown import markdown
import bleach
from slugify import slugify
from .helpers.img_handler import delete_img


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

    @property
    def created_on(self):
        day = self.created_at.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return self.created_at.strftime(f"{day}{suffix}, %b %Y")
    
    @property
    def updated_on(self):
        day = self.updated_at.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return self.updated_at.strftime(f"{day}{suffix}, %b %Y")

    def save(self):
        """Save instance to database."""
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def save_all(records):
        """Save all records to database."""
        db.session.add_all(records)
        db.session.commit()

    @classmethod
    def create(cls, return_=False, **kwargs):
        """Create a new record in the table."""
        record = cls(**kwargs)
        # save to database
        record.save()

        if return_:
            return record
    
    @classmethod
    def join(cls, model, column, exec=True):
        query = db.session.query(cls).join(
            model, eval(f'model.id == cls.{column}')
        )

        # execute the query if exec = True
        return query.all() if exec else query

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
        """Fetch all records from the table."""
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

    @classmethod
    def group_by(cls, *select, group_by=None):
        group_by = group_by or cls.id
        return db.session.query(*select).group_by(group_by)

    @property
    def slug(self):
        return slugify(self.title)


class User(UserMixin, BaseModel):
    """Model representing a user instance."""

    __tablename__ = 'users'

    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(255))
    birth_date = db.Column(db.Date)

    # foreign keys
    poet = db.relationship('Poet', backref='users', uselist=False)
    comments = db.relationship('Comment', backref='users', lazy='dynamic', 
                               cascade='all, delete, delete-orphan')

    @property
    def last_login(self):
        return self.updated_on

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

    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id', ondelete='CASCADE'), unique=True)
    email = db.Column(db.String(255), unique=True, index=True)
    gender = db.Column(db.String(10), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String(3000), nullable=True)

    # foreign keys
    resources = db.relationship('Resource', backref="poets", lazy='dynamic',
                                cascade='all, delete, delete-orphan')
    poems = db.relationship('Poem', backref='poets', lazy='dynamic',
                            cascade='all, delete, delete-orphan')

    @property
    def became_poet_on(self):
        """Return the date that user became a poet."""
        return self.created_on

    @property
    def poet_name(self):
        """Return the poet username."""
        user = User.find_by(id=self.user_id, one=True)
        return user.username

    @classmethod
    def reached_limit(cls):
        """Limit the number of registered poets that can be verified."""
        poets_count = cls.query.filter_by(verified=True).count()
        max_poets_count = current_app.config['MAXIMUM_POET_COUNT']

        return True if poets_count >= max_poets_count else False

    @classmethod
    def get_choices(cls):
        return [(poet.poet_name, poet.poet_name.capitalize())
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
        category = cls.find_by(name=name, one=True)
        return category.id if category else None

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

    @classmethod
    def find_poem_by_slug(cls, slugname):
        for poem in cls.find_all():
            if poem.slug == slugname:
                return poem
        return None


class Stanza(BaseModel):
    """Model representing a stanza of a poem."""

    __tablename__ = 'stanzas'

    poem_id = db.Column(db.String(255), db.ForeignKey(
        'poems.id', ondelete='CASCADE'))
    index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    @property
    def added_on(self):
        return self.created_on

    @property
    def edited_on(self):
        return self.updated_on


class Comment(BaseModel):
    """Model representing a comment made by a user on a poem."""

    __tablename__ = 'comments'

    user_id = db.Column(db.String(255), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    poem_id = db.Column(db.String(255), db.ForeignKey(
        'poems.id', ondelete='CASCADE'))
    comment = db.Column(db.String(255), nullable=False)
    approved = db.Column(db.Boolean, default=False)

    @property
    def last_edit(self):
        return self.updated_on


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


class Resource(BaseModel):
    """Represents a resource added by a poet."""

    __tablename__ = 'resources'

    class ResourceTypes(Enum):
        LINK = 0
        IMAGE = 1
        BRIEF = 2
        COURSE = 3

    rtype = db.Column(db.Integer, default=ResourceTypes.LINK.value)
    title = db.Column(db.String(255), nullable=False, unique=True)
    body = db.Column(db.String(2000), nullable=False)
    published = db.Column(db.Boolean, default=False)
    body_html = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=True)
    poet_id = db.Column(db.String(255), db.ForeignKey(
        'poets.id', ondelete='CASCADE'))

    @property
    def upvotes(self):
        reactions = Reaction.find_by(reaction_type='UPVOTE',
                                     record_id=self.id)
        return len(reactions)

    @property
    def downvotes(self):
        reactions = Reaction.find_by(reaction_type='DOWNVOTE',
                                     record_id=self.id)
        return len(reactions)

    def has_voted(self):
        """Checks if the current user has voted."""
        reaction = Reaction.find_by(record_id=self.id, user_id=current_user.id,
                                    one=True)
        return reaction.reaction_type if reaction else None

    @classmethod
    def supported_types(cls):
        """Get the supported types of resources."""
        return cls.ResourceTypes.__members__

    @classmethod
    def get_type_key(cls, value):
        """Get the key of a value in the supported types."""
        for key, val in cls.supported_types().items():
            if val.value == value:
                return key
        return None

    @classmethod
    def is_type_supported(cls, t: str):
        """Return whether a given type is supported or not."""
        return cls.ResourceTypes.__contains__(t.upper())

    @classmethod
    def get_type_value(cls, t):
        """Return the value of the key passed as resource type."""
        rt = cls.ResourceTypes.__members__.get(t, None)
        return rt.value if rt is not None else None

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'h4', 'h5', 'p', 'u', 'del',
            's', 'sup', 'sub'
        ]


        if Resource.get_type_key(target.rtype) == 'IMAGE':
            if oldvalue and not hasattr(oldvalue, 'NO_VALUE'):
                # delete the existing image
                delete_img(oldvalue)
        else:
            if value:
                # parse the value into html and save to body_html
                target.body_html = bleach.linkify(bleach.clean(markdown(
                    value, output_format='html'),
                    tags=allowed_tags, strip=True
                ))
    
    @staticmethod
    def on_delete_listener(mapper, connection, target):
        # call the on_change_body to remove any image from filesystem
        Resource.on_changed_body(target, None, target.body, None)

    @property
    def is_accessible(self):
        """Check if current user is authorized to manipulate resource."""
        if current_user.is_poet:
            poet = Poet.find_by(user_id=current_user.id, one=True)
            if self.poet_id == poet.id:
                return True
        return False


class Reaction(BaseModel):
    """Represent a user who votes on a resource."""

    __tablename__ = 'reactions'

    class ReactionTypes:
        UPVOTE = 'UPVOTE'
        DOWNVOTE = 'DOWNVOTE'
        RATE = 'RATE'

    user_id = db.Column(db.String(255), db.ForeignKey('users.id',
                                                      ondelete='CASCADE'))
    reaction_type = db.Column(db.String(16), nullable=False)
    # holds the id of the object of user's reaction e.g poem or resource.
    record_id = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float(precision=1), default=0.0)

    @classmethod
    def get_types(cls):
        return {k: v for k, v in cls.ReactionTypes.__dict__
                if not k.startswith('_')}


# load user into the login manager if user exists.
@login_manager.user_loader
def load_user(user_id):
    """Get user data from database."""
    return User.find_by(id=user_id, one=True)


# add event listeners
db.event.listen(Resource.body, 'set', Resource.on_changed_body)
db.event.listen(Resource, 'before_delete', Resource.on_delete_listener)