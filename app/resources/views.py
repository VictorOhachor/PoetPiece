from . import resources
from flask_login import login_required, current_user
from flask import (render_template, url_for, redirect, request,
                   flash, send_from_directory, current_app)
from .forms import ResourceForm
from .manager import manager
from ..models import Resource, Poet
from ..utils import is_poet
import os


@resources.route('/resources')
@login_required
def index():
    """Get all resources created by all poets."""
    r_type = request.args.get('type', 'LINK')
    itype = Resource.get_type_value(r_type)

    context = {
        'resources': manager.find_by_type(itype, True),
    }

    return render_template('resources/index.html', **context)


@resources.route('/resources/create', methods=['GET', 'POST'])
@is_poet
def create_resource():
    """Create a new resource."""
    # set body based on resource type from query
    ResourceForm.set_body()
    # context to be passed to template
    context = dict(
        form=ResourceForm(),
    )

    if context['form'].validate_on_submit():
        form_data = context['form'].data
        return manager.create(form_data)

    return render_template('resources/create_resource.html', **context)


@resources.route('/resources/update', methods=['GET', 'POST'])
@is_poet
def update_resource():
    """Update an existing resource."""
    resource_id = request.args.get('resource_id')
    rtype = request.args.get('type', '')

    # fetch resource from db
    resource = Resource.find_by(id=resource_id, one=True)
    if not resource:
        flash('No resource with given id.', 'error')
        return redirect(url_for('.index', type=rtype))

    # set the body of the resource form
    ResourceForm.set_body()
    context = dict(
        form=ResourceForm(obj=resource)
    )

    if context['form'].validate_on_submit():
        context['form'].populate_obj(resource)
        resource.save()
        flash(f'{rtype} resource has been updated successfully.')
        return redirect(url_for('.index', type=rtype))

    return render_template('resources/create_resource.html', **context)


@resources.route('/resources/delete')
@is_poet
def delete_resource():
    """Remove an existing resource."""
    resource_id = request.args.get('resource_id')
    rtype = request.args.get('type', '')

    if not resource_id:
        flash('Resource id was not provided.', 'error')
    else:
        resource = Resource.find_by(id=resource_id, one=True)
        if not resource:
            flash('Resource with given id was not found', 'error')
        else:
            manager.delete_img(resource.body)
            resource.delete()
            flash(f'{rtype} resource deleted successfully.')
    return redirect(url_for('resources.index', type=rtype))


@resources.route('/resources/<string:resource_id>/vote')
@login_required
def vote_resource(resource_id):
    """Upvote or downvote a resource."""
    status = manager.vote(resource_id)
    rtype = request.args.get('type', 'LINK')
    
    if status:
        flash('Your vote has has made a difference!')
    else:
        flash('Something went wrong. Could not vote.', 'error')
    return redirect(url_for('.index', type=rtype))


@resources.route('/resources/publish')
@is_poet
def publish_resource():
    """Publish or unpublish a resource."""
    resource_id = request.args.get('resource_id')
    rtype = request.args.get('type', 'LINK')

    try:
        resource = Resource.find_by(id=resource_id, one=True)
        if not resource:
            flash('Resource with given id was not found', 'error')
        else:
            resource.published = not resource.published
            resource.save()

            flash(
                f"Successfully {'P' if resource.published else 'Unp'}ublished resource.")
    except Exception as e:
        flash(str(e), 'error')
    finally:
        return redirect(url_for('.index', type=rtype))
