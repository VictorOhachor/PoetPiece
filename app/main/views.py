from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, login_user, logout_user, current_user
from . import main
from .. import db
from .forms import (LoginForm, SignupForm, PoetForm,
                    UpdatePasswordForm, EditProfileForm)
from ..models import User, Poet, Notification
from ..utils import _perform_post, create_notification


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
        # create notification
        n_content = f'{user.username} just signed up!'
        create_notification(n_content, 'AUTH', user.id)
        # redirect user to login page or dashboard.
        flash('You can now login.')
        return redirect(url_for('.login'))

    return render_template('main/signup.html', form=form)


@main.get('/notifications')
@login_required
def notifications():
    """Get all feature/app updates."""
    # extract query parameters
    q = request.args.get('q')
    unread = request.args.get('unread')
    # fetch notifications
    n = Notification.find_order_by(Notification.unread.desc(), 
                                   Notification.created_at.desc(),
                                   in_trash=False)
    return render_template('main/notifications.html', notifications=n)


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
    if context['password_form'].validate_on_submit():
        return _perform_post(context['password_form'], context['_poetic_user'])
    
    if context['profile_form'].validate_on_submit():
        return _perform_post(context['profile_form'], context['_poetic_user'])

    return render_template('main/me.html', **context)


@main.route('/me/become-poet', methods=['GET', 'POST'])
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
            user_id=current_user.id,
            bio=form.bio.data
        )
        # save to database
        poet.save()
        # create notification
        n_content = f'{current_user.username} just became a poet!'
        create_notification(n_content, 'POET', current_user.id)
        # redirect to the profile view
        flash('Aha! Now, you are in your poetic shoes!')
        return redirect(url_for('.me'))

    return render_template('main/poet_form.html', form=form)

@main.get('/me/delete-account')
@login_required
def delete_me():
    """Remove a user's account from db (if user is not a poet)."""
    user = User.find_by(id=current_user.id, one=True)
    n_content = ''

    if user.is_poet:
        poet = Poet.find_by(user_id=user.id, one=True)

        if poet.poems.all():
            err_msg = 'So unfortunate! We will need more information before ' \
                'we can progress with this operation!'
            flash(err_msg, 'error')
            # redirect to the handle survey route
            return redirect(url_for('.handle_survey', type='account_deletion'))
        
        # delete poet account otherwise
        n_content += f'{poet.poet_name} is no longer a poet piece!'
        poet.delete()
    else:
        # create notification
        n_content = f'{user.username} is no longer a PoetPiece user!'
    
    # delete user's account if not a poet
    user.delete()
    # create new notification
    create_notification(n_content, 'USER', user.id)
    # redirect user back to home
    flash("Sorry to see you go; You couldn't even enjoy the poetic privileges!")

    return redirect(url_for('.index'))


@main.get('/surveys/<string:type>')
@login_required
def handle_survey(type):
    """Handles different types of surveys. COMING SOON!"""
    return render_template('main/survey.html', survey_title='Account Deletion')
