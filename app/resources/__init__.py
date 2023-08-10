from flask import Blueprint

resources = Blueprint('resources', __name__, url_prefix='/resources')

from . import views

# register url endpoints
resources.add_url_rule('/', view_func=views.IndexView.as_view('index'), methods=['GET', 'POST'])
resources.add_url_rule('/create', view_func=views.ResourceCreationView.as_view('create_resource'), methods=['GET', 'POST'])
resources.add_url_rule('/update', view_func=views.ResourceUpdateView.as_view('update_resource'), methods=['GET', 'POST'])
resources.add_url_rule('/delete', view_func=views.ResourceDeletionView.as_view('delete_resource'), methods=['GET'])
resources.add_url_rule('/<string:resource_id>/vote', view_func=views.ResourceVoteView.as_view('vote_resource'), methods=['GET'])
resources.add_url_rule('/publish', view_func=views.ResourcePublishView.as_view('publish_resource'), methods=['GET'])
