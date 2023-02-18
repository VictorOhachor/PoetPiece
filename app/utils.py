"""Contain utility or helper functions and decorators."""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def is_admin(func):
    """Protect view function from users that are not admins."""
    @wraps(func)
    def wrapper(**kwargs):
        if not current_user.is_admin:
            flash('You are not authorized to access this page.', 'error')
            # redirect to different urls based on referrer
            if not kwargs:
                return redirect(url_for('show_poems'))
            return redirect(url_for('show_poem', **kwargs))
        return func(**kwargs)

    return wrapper
