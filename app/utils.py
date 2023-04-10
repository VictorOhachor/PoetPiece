"""Contain utility or helper functions and decorators."""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required
from .models import Poem
from . import db


def is_poet(func):
    """Protect view function from users that are not poets."""
    @wraps(func)
    @login_required
    def wrapper(**kwargs):
        if not current_user.is_poet:
            flash('You are not authorized to access this page.', 'error')
            # redirect to different urls based on referrer
            if not kwargs:
                return redirect(url_for('poems.index'))
            return redirect(url_for('poems.poem', **kwargs))
        return func(**kwargs)
    return wrapper


def can_manage_poem(poem_id):
    """Check if current user can manipulate poem."""
    poem = Poem.query.get_or_404(poem_id, 'Poem with such id was not found.')
    return poem.is_accessible


def _perform_post(context, form_name):
    """Perform post operation on form."""
    form = context.get(form_name, None)

    if form and form.validate_on_submit():
        [form.populate_obj(item) for item in context['_poetic_user']]
        # persist changes to db
        db.session.add_all(context['_poetic_user'])
        db.session.commit()
        
        # redirect back to me
        flash('Successfully updated your password.')
        return redirect(url_for('.me'))
