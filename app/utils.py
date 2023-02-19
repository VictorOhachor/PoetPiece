"""Contain utility or helper functions and decorators."""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required
from uuid import uuid4


def is_admin(func):
    """Protect view function from users that are not admins."""
    @wraps(func)
    @login_required
    def wrapper(**kwargs):
        if not current_user.is_admin:
            flash('You are not authorized to access this page.', 'error')
            # redirect to different urls based on referrer
            if not kwargs:
                return redirect(url_for('show_poems'))
            return redirect(url_for('show_poem', **kwargs))
        return func(**kwargs)

    return wrapper


def generate_id():
    """Generate a uuid and return the 32-char string."""
    uid = uuid4()
    return uid.hex


def get_category_choices(c, db):
    """Fetch the list of category names from the database."""
    return [(category[0], category[0].upper())
            for category in db.session.query(
        c.name).all()]
