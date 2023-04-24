from . import resources
from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request
from .forms import ResourceForm
from .manager import manager


@resources.route('/resources')
@login_required
def index():
    """Get all resources created by all poets."""
    pass


@resources.route('/resources/create', methods=['GET', 'POST'])
@login_required
def create_resource():
    """Create a new resource."""
    # set body based on resource type from query
    ResourceForm.set_body()
    # context to be passed to template
    context = dict(
        form=ResourceForm(),
        types_icons=['link', 'image', 'message', 'book'],
    )

    if context['form'].validate_on_submit():
        form_data = context['form'].data
        return manager.create(form_data)

    return render_template('resources/create_resource.html', **context)
