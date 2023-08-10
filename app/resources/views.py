from . import resources
from flask.views import MethodView
from flask_login import login_required
from flask import render_template, url_for, redirect, request, flash, g
from .forms import ResourceForm
from .controllers import ResourceController
from ..models import Resource
from ..utils import is_poet
from ..helpers.img_handler import delete_img

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
            success = controllers.create_resource(form.data)

            if success:
                return redirect(url_for('.index', type=r_type))
        
        for error in form.errors.items():
            flash(error[1][0], 'error')
            break

        return redirect(url_for('.create_resource', type=r_type))


class ResourceUpdateView(MethodView):
    decorators = [is_poet]

    def dispatch_request(self, *args, **kwargs):
        self.resource_id = request.args.get('resource_id')
        self.r_type = request.args.get('type')

        return super().dispatch_request(*args, **kwargs)

    def get(self):
        assert self.resource_id and self.r_type
        
        resource = Resource.find_by(id=self.resource_id, one=True)

        if not resource:
            flash('No resource found with given id', 'error')
            return redirect(url_for('.index', type=self.r_type))
        
        g.form = ResourceForm.create(resource)
        g.update = True

        return render_template('resources/create_resource.html')
    
    def post(self):
        assert self.resource_id and self.r_type
        
        form = ResourceForm.create()

        if form.validate_on_submit():
            success = controllers.update_resource(
                self.resource_id, form.data
            )

            if success:
                return redirect(url_for('.index', type=self.r_type))

        for error in form.errors.items():
            flash(error[1][0], 'error')
            break
        
        return redirect(url_for('.update_resource', type=self.r_type,
                                resource_id=self.resource_id))


class ResourceDeletionView(MethodView):
    decorators = [is_poet]

    def get(self):
        """Remove an existing resource."""
        resource_id = request.args.get('resource_id')
        rtype = request.args.get('type', '') 

        if not resource_id:
            flash('Resource id was not provided.', 'error')
        else:
            success = controllers.delete_resource(resource_id)

        return redirect(url_for('.index', type=rtype))


class ResourceVoteView(MethodView):
    decorators = [login_required]

    def get(self, resource_id):
        """Upvote or downvote a resource"""
        resource = Resource.find_by(id=resource_id, one=True)
        rtype = Resource.get_type_key(resource.rtype) or 'LINK'

        # vote on the resource
        success = controllers.vote(resource_id)

        if success:
            flash('Your vote definitely made a significant difference!')
        else:
            flash('Your vote was not casted as something went wrong', 'error')
        
        return redirect(url_for('.index', type=rtype))
    

class ResourcePublishView(MethodView):
    decorators = [is_poet]

    def get(self):
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

        return redirect(url_for('.index', type=rtype))
