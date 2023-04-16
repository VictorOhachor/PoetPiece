"""Contain utility or helper functions and decorators."""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required
from .models import Poem, Notification, Poet, User
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


def _perform_post(form, poetic_user: list):
    """Perform post operation on form."""

    [form.populate_obj(item) for item in poetic_user]
    # persist changes to db
    db.session.add_all(poetic_user)
    db.session.commit()

    # redirect back to me
    form_type = form._prefix.split('_')[0]
    flash(f'Successfully updated your {form_type}.')
    return redirect(url_for('.me'))


def create_notification(content, ntype, user_id=None):
    try:
        # extract notification data
        n_data = {'content': content, 'type_': ntype}
        if user_id:
            n_data['user_id'] = user_id
        # create notification
        Notification.create(**n_data)
    except Exception as e:
        print(str(e))


def _process_search_query(form_data: dict):
    """Process the form data passed and returned a more refined dict data."""
    refined_data = {}
    # all search/filter query keys that will be used
    queryKeys = [('q', str), ('author_id', str), ('rating', int), 
                 ('completed', bool), ('premium', bool)]

    if form_data.get('poet'):
        refined_data['author_id'] = Poet.find_by(user_id=User.find_by_username(
            form_data['poet']).id, one=True).id
    
    for key, converter in queryKeys:
        value = form_data.get(key)
        if value and key not in refined_data:
            if converter == bool:
                refined_data[key] = True if value == 'True' else False
            else:
                refined_data[key] = converter(value)
    
    return refined_data
