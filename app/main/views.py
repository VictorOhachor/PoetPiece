from flask.views import MethodView
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_required
from . import main
from ..models import Poet
from .forms import LoginForm, SignupForm, PoetForm
from .controllers import MainController

# Create the main controller
controllers = MainController()


class IndexView(MethodView):
    def get(self):
        """Return user to the home page"""
        return render_template('index.html')


class LoginView(MethodView):
    def get(self):
        form = LoginForm()

        if current_user.is_authenticated:
            flash('I know who you are; logging you in now...')
            return redirect(url_for('poems.index'))
        
        return render_template('main/login.html', form=form)
    
    def post(self):
        form = LoginForm()

        if form.validate_on_submit():
            # authenticate user with given username and password
            res = controllers.authenticate_user(
                form.username.data,
                form.password.data,
                form.remember_me.data
            )

            if res:
                return res

        return render_template('main/login.html', form=form)


class SignupView(MethodView):
    def get(self):
        """Show user the signup page"""
        return render_template('main/signup.html', form=SignupForm())
    
    def post(self):
        form = SignupForm(request.form)

        if form.validate_on_submit():
            return controllers.create_user(
                username=form.username.data,
                password=form.password.data,
                birth_date=form.birth_date.data
            )
        
        return render_template('main/signup.html', form=form)


class LogoutView(MethodView):
    decorators = [login_required,]

    def get(self):
        """Log user out of the application"""
        logout_user()

        flash('You chose to log out.')
        return redirect(url_for('.index'))


class ProfileView(MethodView):
    decorators = [login_required, ]

    def get(self):
        """Display user's profile."""
        context = controllers.get_profile()
        return render_template('main/me.html', **context)
    
    def post(self):
        """Update user's profile or password."""
        return controllers.update_profile()


class BecomePoetView(MethodView):
    decorators = [login_required]

    def get(self):
        """Get the form used to create new poet."""
        form = PoetForm()
        return render_template('main/poet_form.html', form=form)
    
    def post(self):
        if Poet.reached_limit():
            flash('At the moment, set maximum limit of poets reached', 'error')
            return redirect(request.referrer)
        
        return controllers.create_poet()


class DeleteUserView(MethodView):
    decorators = [login_required]

    def get(self):
        """Delete a user's account"""
        return controllers.delete_account()


class SurveyView(MethodView):
    decorators = [login_required]

    def get(self):
        """Handles different types of surveys. COMING SOON!"""
        return render_template('main/survey.html', survey_title='Account Deletion')


# Add endpoints for the views
main.add_url_rule('/', view_func=IndexView.as_view('index'), methods=['GET'])
main.add_url_rule('/login', view_func=LoginView.as_view('login'), methods=['GET', 'POST'])
main.add_url_rule('/signup', view_func=SignupView.as_view('signup'), methods=['GET', 'POST'])
main.add_url_rule('/logout', view_func=LogoutView.as_view('logout'), methods=['GET'])
main.add_url_rule('/me', view_func=ProfileView.as_view('me'), methods=['GET', 'POST'])
main.add_url_rule('/become-poet', view_func=BecomePoetView.as_view('become_poet'), methods=['GET', 'POST'])
main.add_url_rule('/delete-account', view_func=DeleteUserView.as_view('delete_me'), methods=['GET'])
main.add_url_rule('/take-survey', view_func=LoginView.as_view('handle_survey'), methods=['GET', 'POST'])
