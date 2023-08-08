from flask import Blueprint

main = Blueprint('main', __name__)

from . import views

# Add endpoints for the views
main.add_url_rule('/', view_func=views.IndexView.as_view('index'), methods=['GET'])
main.add_url_rule('/login', view_func=views.LoginView.as_view('login'), methods=['GET', 'POST'])
main.add_url_rule('/signup', view_func=views.SignupView.as_view('signup'), methods=['GET', 'POST'])
main.add_url_rule('/logout', view_func=views.LogoutView.as_view('logout'), methods=['GET'])
main.add_url_rule('/me', view_func=views.ProfileView.as_view('me'), methods=['GET', 'POST'])
main.add_url_rule('/me/view-as-user', view_func=views.PoetView.as_view('preview_profile'), methods=['GET'])
main.add_url_rule('/become-poet', view_func=views.BecomePoetView.as_view('become_poet'), methods=['GET', 'POST'])
main.add_url_rule('/delete-account', view_func=views.DeleteUserView.as_view('delete_me'), methods=['GET'])
main.add_url_rule('/take-survey', view_func=views.LoginView.as_view('handle_survey'), methods=['GET', 'POST'])
