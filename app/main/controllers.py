from flask import flash, redirect, url_for, render_template, request
from flask_login import current_user, login_user
from .. import db
from ..models import User, Poet
from datetime import timedelta
from .forms import PoetForm, UpdatePasswordForm, EditProfileForm

class MainController:

    def delete_account(self):
        """Remove a user's account from db."""
        user = User.find_by(id=current_user.id, one=True)

        if user and user.is_poet:
            poet = Poet.find_by(user_id=user.id, one=True)

            if poet.poems.all():
                flash('To proceed with this operation, please delete all your poems.')
                # redirect to the handle_survey endpoint
                return redirect(url_for('.handle_survey', type='account_deletion'))
            
            # delete poet account otherwise
            poet.delete()
        
        # delete user's account
        user.delete()

        flash('Sorry to see you go 🥹!')
        return redirect(url_for('.index'))
    
    def create_poet(self):
        """Create a new poet account for a registered user"""
        form = PoetForm(request.form)
        
        # for POST requests
        if form.validate_on_submit():
            poet = Poet(
                bio=form.data['bio'],
                gender=form.data['gender'],
                email=form.data['email'],
                user_id=current_user.id,
            )
            poet.save()

            flash ('Congratulations on joining the PoetPiece squad!')
            return redirect(url_for('.me'))
            
        return render_template('main/poet_form.html', form=form)


    def get_profile(self, init_form=True):
        """Get a user profile from the database"""
        p_user = db.session.query(User, Poet).filter(
            User.id == Poet.user_id, User.id == current_user.id).first()
        
        if not p_user:
            p_user = [User.find_by(id=current_user.id, one=True), ]

        form_data = {}

        for instance in p_user:
            form_data.update(**instance.to_dict())

        return {
            'form_data': form_data,
            'user': p_user,
            'password_form': UpdatePasswordForm(prefix='password_form'),
            'profile_form': EditProfileForm(
                **form_data if init_form else request.form, prefix='profile_form'
            )
        }
    
    def _update_user_profile(self, form, p_user: list):
        """Perform post operation on form."""
        form_type = form._prefix.split('_')[0]
        
        try:
            for user in p_user:
                form.populate_obj(user)

            # persist changes to db
            db.session.add_all(p_user)
            db.session.commit()

            # redirect back to referrer url
            flash(f'Your {form_type} has been updated')
        except:
            flash(f'Failed to update your {form_type}; try again')
    
    def update_profile(self):
        context = self.get_profile(False)
        forms = [value for key, value in context.items() if key.endswith('form')]

        for form in forms:
            if form.validate_on_submit():
                self._update_user_profile(form, context['user'])
                break
        
        return redirect(request.referrer)
    
    def create_user(self, **kwargs):
        """Create a new user"""
        user = User(**kwargs)
        user.save()

        # log user in automatically
        login_user(user, True, timedelta(seconds=3600))

        return redirect(url_for('poems.index'))
    
    def authenticate_user(self, username, password, remember=False):
        """Log a user into PoetPiece"""
        user = User.find_by_username(username)

        if user and user.verify_password(password):
            login_user(user, remember)

            # determine where to redirect user to
            next = request.args.get('next')
            if not (next and next.startswith('/')):
                next = request.referrer
            
            return redirect(next)

        flash('The username or password you provided is incorrect', 'error')
        return False
