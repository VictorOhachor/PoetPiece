from flask import Blueprint

poems = Blueprint('poems', __name__, url_prefix='/poems')

from . import views

# Add endpoints for the views
poems.add_url_rule('/', view_func=views.IndexView.as_view('index'), methods=['GET'])
poems.add_url_rule('/search', view_func=views.SearchPoemsView.as_view('search'), methods=['GET', 'POST'])
poems.add_url_rule('/categories', view_func=views.CategoryMutationView.as_view('mutate_categories'), methods=['GET', 'POST'])
poems.add_url_rule('/new', view_func=views.PoemCreationView.as_view('create_poem'), methods=['GET', 'POST'])
poems.add_url_rule('/<string:poem_id>', view_func=views.PoemView.as_view('poem_by_id'), methods=['GET', 'POST'])
poems.add_url_rule('/s/<string:slugname>', view_func=views.PoemView.as_view('poem_by_slug'), methods=['GET', 'POST'])
poems.add_url_rule('/<string:poem_id>/poet', view_func=views.PoetView.as_view('view_poet'), methods=['GET'])
poems.add_url_rule('/<string:poem_id>/edit', view_func=views.PoemEditView.as_view('edit_poem'), methods=['GET', 'POST'])
poems.add_url_rule('/<string:poem_id>/delete', view_func=views.PoemDeletionView.as_view('delete_poem'), methods=['GET'])
poems.add_url_rule('/<string:poem_id>/add_stanza', view_func=views.StanzaCreationView.as_view('add_stanza'), methods=['GET', 'POST'])
poems.add_url_rule('/<string:poem_id>/stanzas/<string:stanza_id>/delete', view_func=views.StanzaDeletionView.as_view('delete_stanza'), methods=['GET'])
poems.add_url_rule('/<string:poem_id>/stanzas/<string:stanza_id>/edit', view_func=views.StanzaEditView.as_view('edit_stanza'), methods=['GET', 'POST'])
poems.add_url_rule('/<string:poem_id>/comments/<string:comment_id>/delete', view_func=views.CommentDeletionView.as_view('delete_comment'), methods=['GET'])
poems.add_url_rule('/<string:poem_id>/publish', view_func=views.PoemPublishView.as_view('publish_poem'), methods=['GET'])
poems.add_url_rule('/<string:poem_id>/complete', view_func=views.CompletePoemView.as_view('complete_poem'), methods=['GET'])
