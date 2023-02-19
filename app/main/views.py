from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, login_user, logout_user, current_user
from . import main
from .. import db
from .forms import LoginForm, SignupForm
from ..models import User, Admin


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
    records = []  # contains the User (and perhaps Admin) instance(s)

    try:
        if form.validate_on_submit():
            is_admin = form.is_admin.data

            user = User(username=form.username.data,
                        password=form.password.data,
                        birth_date=form.birth_date.data)
            records.append(user)

            if is_admin:
                # retrieve email and gender date
                email = form.email.data
                gender = form.gender.data

                if Admin.reached_admin_count():
                    flash(
                        'Restricted: The number of registered admins has reached limit.',
                        'error')
                    return redirect(url_for('.signup'))

                if not (email and gender):
                    flash('Email and gender are required for an admin account.', 'error')
                    return redirect(url_for('.signup'))

                records.append(
                    Admin(
                        email=email,
                        gender=gender,
                        users=user
                    ))
                user.is_admin = True

            # persist to database
            db.session.add_all(records)
            db.session.commit()

            # redirect to login page
            flash('You can now login.')
            return redirect(url_for('.login'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('.signup'))

    return render_template('main/signup.html', form=form)
