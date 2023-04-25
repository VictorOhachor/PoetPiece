from ..models import Resource, Poet
from flask import flash, redirect, url_for, current_app, request
from flask_login import current_user
from flask_wtf.file import FileStorage
from werkzeug.utils import secure_filename
from uuid import uuid4
import os


class ResourceManager:
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

    def _handle_img(self, body):
        """Handle the image passed to it and return the image path."""
        if isinstance(body, FileStorage):
            filename = 'resources/' + f'{uuid4().hex}_' + secure_filename(
                body.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']

            # create directory if it doesn't exist
            resources_path = os.path.join(upload_folder,
                                          filename.split('/')[0])
            if (not os.path.exists(resources_path)):
                os.makedirs(resources_path, exist_ok=True)

            # construct image path
            img_path = os.path.join(upload_folder,
                                    filename)
            # SAVE image to filesystem
            body.save(img_path)

            return url_for('static', filename=f'uploads/{filename}')
        raise TypeError('Body is not an image!')

    def delete_img(self, filename):
        """Delete an image from the filesystem if it exist."""
        upload_folder = current_app.config['UPLOAD_FOLDER']
        img_path = os.path.join(upload_folder, '../../', filename)

        if os.path.exists(img_path):
            os.remove(img_path)
            return True
        return False

    def _extract_data(self, data):
        """Extract resource data from form data."""
        supported_keys = ['rtype', 'title', 'body', 'published']

        formatted_data = {
            key: self._handle_img(data[key])
            if self.is_image_body(key, data) else data[key]
            for key in supported_keys
        }

        # add the poet_id to the formatted data
        poet = Poet.find_by(user_id=current_user.id,
                            one=True)
        if not poet:
            raise TypeError('You don\'t have poetic privileges!')
        formatted_data['poet_id'] = poet.id

        return formatted_data

    def create(self, data: dict):
        """Create a resource."""
        r_type = request.args.get('type', 'LINK')
        try:
            r_data = self._extract_data(data)
            self.model.create(**r_data)
            flash(f'{r_type} resource successfully created.')
        except Exception as e:
            flash(str(e), 'error')
        finally:
            return redirect(url_for('resources.create_resource', type=r_type))

    def find_by_type(self, itype, sort=False):
        """Find resources by numerical resource type."""
        db_query = self.model.query

        if current_user.is_poet:
            # fetch the poet account
            poet = Poet.find_by(user_id=current_user.id, one=True)
            # query db for resources based on type
            db_query = db_query.filter(
                (Resource.rtype == itype) & (
                    (Resource.published == True) | (
                        (Resource.poet_id == poet.id) & (
                            Resource.published == False)
                    )
                )
            )
        else:
            db_query = db_query.filter_by(published=True)

        if sort:
            db_query = db_query.order_by(Resource.title,
                                         Resource.upvotes.desc())

        return db_query.all()


manager = ResourceManager()