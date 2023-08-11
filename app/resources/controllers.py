from ..models import Resource, Poet, Reaction
from flask import flash, redirect, url_for, current_app, request
from flask_login import current_user
from .. import db
from flask_wtf.file import FileStorage
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
from hashlib import md5
from ..helpers.img_handler import delete_img


class ResourceController:
    """Provide a user-friendly API for managing resources."""

    def __init__(self):
        self.model = Resource

    @property
    def resources(self):
        return self.model.find_all()

    @property
    def most_recent(self):
        return self.resources[-1] if self.resources else None

    def is_image_body(self, key, data):
        """Check if the key is body and the data is for image resource."""
        if data['rtype'] == self.model.supported_types().get('IMAGE').value \
                and key == 'body':
            return True
        return False

    def __save_uploaded_image(self, file_storage, custom_dir='resources'):
        """Handle the image passed to it and return the image path."""
        if not isinstance(file_storage, FileStorage):
            raise TypeError('Body is not an image!')
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        file_hash = md5(file_storage.read()).hexdigest()
        filename = f'{file_hash}_{secure_filename(file_storage.filename)}'

        # construct the complete path to save the image
        img_path = os.path.join(upload_folder, custom_dir, filename)

        # create the directory where image will be stored if necessary
        os.makedirs(os.path.dirname(img_path), exist_ok=True)

        # save the image to the filesystem
        file_storage.seek(0)
        file_storage.save(img_path)

        # Generate and return the URL for the saved image
        return url_for('static', filename=f'uploads/{custom_dir}/{filename}')

    def _extract_data(self, data):
        """Extract resource data from form data."""
        supported_keys = ['rtype', 'title', 'body', 'published']

        formatted_data = {
            key: self.__save_uploaded_image(data[key])
            if self.is_image_body(key, data) else data[key]
            for key in supported_keys
        }

        # add the poet_id to the formatted data
        poet = Poet.find_by(user_id=current_user.id,
                            one=True)
        if not poet:
            raise TypeError("You don't have poetic privileges!")
        formatted_data['poet_id'] = poet.id

        return formatted_data

    def create_resource(self, data: dict):
        """Create a resource."""
        r_type = request.args.get('type', 'LINK')

        try:
            r_data = self._extract_data(data)
            self.model.create(**r_data)
            
            flash(f'{r_type} resource successfully created.')
            return True
        except Exception as e:
            flash(str(e), 'error')
        
        return False
    
    def update_resource(self, resource_id: str, data: dict):
        """Update an existing resource"""
        try:
            r_data = self._extract_data(data)
            resource = Resource.find_by(id=resource_id, one=True)

            # update the resource
            resource.body = r_data.get('body', resource.body)
            resource.title = r_data.get('title', resource.title)
            resource.published = r_data.get('published', resource.published)

            # commit the database changes
            resource.save()
          
            flash(f'Resource "{r_data["title"][:10]}..." has been updated successfully')
            return True
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'error')
        
        return False

    def find_by_type(self, itype, sort=False):
        """Find resources by numerical resource type."""
        db_query = self.model.query

        if itype is not None:
            if current_user.is_poet:
                # fetch the poet account
                poet = Poet.find_by(user_id=current_user.id, one=True)
                # query db for resources based on type
                db_query = db_query.filter(
                    (Resource.rtype == itype) & ((Resource.published == True) | (
                        (Resource.poet_id == poet.id) & (Resource.published == False))))
            else:
                db_query = db_query.filter_by(rtype=itype, published=True)

        if sort:
            # order by title ascending
            db_query = db_query.order_by(Resource.title)
        else:
            # order by latest
            db_query = db_query.order_by(Resource.created_at.desc())

        return db_query.all()

    def vote(self, resource_id):
        """Upvote or downvote a resource."""
        downvote = request.args.get('downvote')
        vote_type = 'DOWNVOTE' if downvote is not None else 'UPVOTE'

        resource = self.model.find_by(id=resource_id, one=True)
        if not resource:
            return False

        reaction = Reaction.find_by(record_id=resource.id,
                                    user_id=current_user.id, one=True)
        
        if reaction:
            reaction.reaction_type = vote_type
            reaction.save()
        else:
            Reaction.create(user_id=current_user.id, reaction_type=vote_type,
                            record_id=resource.id)
        return True
    
    def delete_resource(self, resource_id):
        resource = Resource.find_by(id=resource_id, one=True)
        
        if not resource:
            flash('Resource with given id was not found', 'error')
        else:
            try:
                # delete the record from the database
                resource.delete()
    
                flash(f'Resource "{resource.title[:10]}..." has been deleted successfully')
                return True
            except Exception as e:
                flash(str(e), 'error')
        
        return False
