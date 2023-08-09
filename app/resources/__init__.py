from flask import Blueprint

resources = Blueprint('resources', __name__, url_prefix='/resources')

from . import views

# register url endpoints
resources.add_url_rule('/', view_func=views.IndexView.as_view('index'), methods=['GET', 'POST'])
resources.add_url_rule('/create', view_func=views.ResourceCreationView.as_view('create_resource'), methods=['GET', 'POST'])
