from . import resources
from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request
from ..models import Resource
from .forms import ResourceForm


@resources.get('/resources')
@login_required
def create_resource():
    """Get all feature/app updates."""
    # set body based on resource type from query
    ResourceForm.set_body()
    # context to be passed to template
    context = dict(
        form=ResourceForm(),
    )

    return render_template('resources/create_resource.html', **context)
