from flask import render_template, redirect, request, flash, url_for, current_app
from flask_login import login_required, login_user, logout_user, current_user
from . import main
from .. import db
from .forms import (LoginForm, SignupForm, AdminSignupForm,
                    UpdatePasswordForm, EditProfileForm)
from ..models import User, Admin
from ..email import send_email


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
        db.session.add(user)
        db.session.commit()
        # send an email notification to app admin
        # send_email(current_app.config['POETICMAN_ADMIN'],
        #            'New User', 'mail/new_user', user=user)
        # redirect to login page
        flash('You can now login.')
        return redirect(url_for('.login'))

    return render_template('main/signup.html', form=form)


@main.route('/create-admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    """Create an admin account for a registered user."""
    form = AdminSignupForm()

    if Admin.reached_admin_count():
        flash('Number of registered admins has reached maximum.', 'error')
        return redirect(url_for('.me'))

    if form.validate_on_submit():
        admin = Admin(
            email=form.email.data,
            gender=form.gender.data,
            user_id=current_user.id
        )
        # Add to session
        db.session.add(admin)
        # persist to database
        db.session.commit()

        token = admin.generate_verification_token()
        send_email(admin.email, 'Verify your poet account',
                   'mail/verify_admin', token=token, admin=admin)
        return redirect(url_for('poems.index'))

    return render_template('main/create_admin.html', form=form)


@main.route('/verify-admin/<token>', methods=['GET', 'POST'])
@login_required
def verify_admin(token):
    """Verify an admin account by sending verification mail to given address."""
    admin = Admin.query.filter_by(user_id=current_user.id).first()

    if admin.verify_account(token):
        db.session.commit()
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.me'))


@main.get('/notifications')
@login_required
def notifications():
    """Get all feature/app updates."""
    pass


@main.route('/me', methods=['GET', 'POST'])
@login_required
def me():
    """Display and update user/admin information."""
    context = {
        'user': User.query.join(Admin, User.id == Admin.user_id, isouter=True)
        .filter(User.id == current_user.id).first(),
        'password_form': UpdatePasswordForm(prefix='password_form')
    }
    context['profile_form'] = EditProfileForm(
        obj=context['user'], prefix='profile_form')

    if context['password_form'].validate_on_submit():
        context['password_form'].populate_obj(context['user'])
        # persist to db
        db.session.add(context['user'])
        db.session.commit()
        # send flash message
        flash('Successfully updated your password.')
        return redirect(url_for('.me'))

    if context['profile_form'].validate_on_submit():
        context['profile_form'].populate_obj(context['user'])
        # persist to db
        db.session.add(context['user'])
        db.session.commit()
        # send flash message
        flash('Your information has been updated successfully.')
        return redirect(url_for('.me'))

    return render_template('main/me.html', **context)


@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search for poems or notifications."""
    pass

