from . import resources
from flask.views import MethodView
from flask_login import login_required
from flask import render_template, url_for, redirect, request, flash, g
from .forms import ResourceForm
from .controllers import ResourceController
from ..models import Resource
from ..utils import is_poet

controllers = ResourceController()

class IndexView(MethodView):
    decorators = [login_required]

    def get(self):
        """Get all resources created by poets by type."""
        r_type = request.args.get('type')
        itype = Resource.get_type_value(r_type)

        g.resources = controllers.find_by_type(itype, True)
        g.r_type = r_type

        return render_template('resources/index.html')


class ResourceCreationView(MethodView):
    decorators = [is_poet]

    def get(self):
        # add the resource type to the context too
        g.r_type = request.args.get('type', 'LINK')

        # add the form to the global context for the request
        g.form = ResourceForm.create()

        return render_template('resources/create_resource.html')
    
    def post(self):
        r_type = request.args.get('type', 'LINK')
        form = ResourceForm.create()

        if form.validate_on_submit():
            success = controllers.create(form.data)

            if success:
                return redirect(url_for('.index', type=r_type))
        
        for error in form.errors.items():
            flash(error[1][0], 'error')
            break

        return redirect(url_for('.create_resource', type=r_type))


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
            controllers.delete_img(resource.body)
            resource.delete()
            flash(f'{rtype} resource deleted successfully.')
    return redirect(url_for('resources.index', type=rtype))


@resources.route('/resources/<string:resource_id>/vote')
@login_required
def vote_resource(resource_id):
    """Upvote or downvote a resource."""
    # get the rtype of a resource.
    resource = Resource.find_by(id=resource_id, one=True)
    rtype = Resource.get_type_key(resource.rtype) or 'LINK'

    # vote on a resource
    status = controllers.vote(resource_id)

    if status:
        flash('Your vote has made a difference!')
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
