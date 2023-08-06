"""Contain utility or helper functions and decorators."""

from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user, login_required
from .models import Poem, Poet, User


def is_poet(func):
    """Protect view function from users that are not poets."""
    @wraps(func)
    @login_required
    def wrapper(**kwargs):
        if not current_user.is_poet:
            flash('You are not authorized to access this page.', 'error')
            # redirect to different urls based on referrer
            if not kwargs:
                return redirect(request.referrer or url_for('.index'))
            return redirect(url_for('poems.poem', **kwargs))
        return func(**kwargs)
    return wrapper


def is_verified_poet(func):
    """Protect a view function from poets that are not verified."""
    @wraps(func)
    @is_poet
    def wrapper(**kwargs):
        poet = Poet.find_by(user_id=current_user.id, one=True)

        if not (poet and poet.verified):
            flash('Only verified poets can create categories.', 'error')
            return redirect(request.referrer or url_for('.index'))
        return func(**kwargs)
    return wrapper


def can_manage_poem(poem_id):
    """Check if current user can manipulate poem."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id was not found.')
    return poem.is_accessible
