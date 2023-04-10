from flask import render_template, redirect, request, flash, url_for, current_app
from flask_login import login_required, login_user, logout_user, current_user
from . import main
from .. import db
from .forms import (LoginForm, SignupForm, PoetForm,
                    UpdatePasswordForm, EditProfileForm)
from ..models import User, Poet
from ..utils import _perform_post


@main.route('/', methods=['GET', 'POST'])
def index():
    """Implement Index View."""
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Implement Login View."""
    form = LoginForm()

    if current_user.is_authenticated:
        flash('Automatically logged you in.')
        return redirect(url_for('poems.index'))

    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('poems.index')
            return redirect(next)
        flash('Invalid username or password.', 'error')
    return render_template('main/login.html', form=form)


@main.get('/logout')
@login_required
def logout():
    """Log user out of the session."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.index'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    """Implement Sign up View."""
    form = SignupForm()

    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    birth_date=form.birth_date.data)
        # persist to database
        user.save()

        flash('You can now login.')
        return redirect(url_for('.login'))

    return render_template('main/signup.html', form=form)


@main.route('/become-poet', methods=['GET', 'POST'])
@login_required
def become_poet():
    """Create an poet account for a registered user."""
    form = PoetForm()

    if Poet.reached_limit():
        flash('Maximum number of poets reached.', 'error')
        return redirect(url_for('.me'))

    if form.validate_on_submit():
        poet = Poet(
            email=form.email.data,
            gender=form.gender.data,
            user_id=current_user.id
        )
        # save to database
        poet.save()
        # redirect to the profile view
        return redirect(url_for('.me'))

    return render_template('main/poet_form.html', form=form)


@main.get('/notifications')
@login_required
def notifications():
    """Get all feature/app updates."""
    pass


@main.route('/me', methods=['GET', 'POST'])
@login_required
def me():
    """Display and update user information."""
    poetic_user = db.session.query(User, Poet).filter(
        User.id == Poet.user_id, User.id == current_user.id
    ).first()

    if not poetic_user:
        poetic_user = [User.find_by(id=current_user.id, one=True), ]
    
    form_data = {}

    for instance in poetic_user:
        form_data.update(**instance.to_dict())

    context = {
        'form_data': form_data,
        'password_form': UpdatePasswordForm(prefix='password_form'),
        '_poetic_user': poetic_user
    }

    context['profile_form'] = EditProfileForm(
        **context['form_data'], prefix='profile_form')

    # perform post operations
    _perform_post(context, 'password_form')
    _perform_post(context, 'profile_form')

    return render_template('main/me.html', **context)


@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search for poems or notifications."""
    pass
