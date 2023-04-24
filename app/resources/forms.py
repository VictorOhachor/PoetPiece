from flask_login import current_user
from flask_wtf import FlaskForm
from flask import request
from wtforms import (StringField, SubmitField, FileField,
                     TextAreaField, URLField, SelectField)
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import (DataRequired, Length)
from wtforms import ValidationError
from ..models import Resource


class ResourceForm(FlaskForm):
    """This is the form for creating resources of different types."""
    body_types = {
        'LINK': URLField('Enter the Link to the External Resource:',
                         validators=[DataRequired(), Length(1, 255)]),
        'IMAGE': FileField('Choose the Image You Want to Upload:',
                           validators=[FileRequired(), FileAllowed([
                               'jpeg', 'jpg', 'png'],
                               'Resource must be an image!')]),
        'BRIEF': TextAreaField('What do You Want to Share with Others?',
                               validators=[DataRequired(), Length(1, 755)],
                               render_kw={'rows': '6'})
    }

    # form fields
    title = StringField('Enter a Title for This Resource:', validators=[
        DataRequired(), Length(1, 255)
    ])
    rtype = SelectField('Resource Type:', choices=[
        (t, name) for t, name in enumerate(Resource.supported_types())
    ], coerce=int)
    submit = SubmitField('Post Resource')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rtype.data = Resource.supported_types().get(self.body_type).value
        self.rtype.render_kw = {'disabled': True}

    @classmethod
    def set_body(cls):
        cls.body_type = request.args.get('type', 'LINK')
        cls.body = cls.body_types.get(cls.body_type)
