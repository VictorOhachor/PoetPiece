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
            filename = secure_filename(body.filename)

            # create directory if it doesn't exist
            resources_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                          'resources')
            if (not os.path.exists(resources_path)):
                os.makedirs(resources_path, exist_ok=True)

            # construct image path
            img_path = os.path.join(resources_path,
                                    f'{uuid4().hex}-{filename}')
            # SAVE image to filesystem
            body.save(img_path)

            return img_path
        raise TypeError('Body is not an image!')

    def _extract_data(self, data):
        """Extract resource data from form data."""
        supported_keys = ['rtype', 'title', 'body']

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


manager = ResourceManager()
