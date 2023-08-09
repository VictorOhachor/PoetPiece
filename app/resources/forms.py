from flask_login import current_user
from flask_wtf import FlaskForm
from flask import request
from wtforms import (StringField, SubmitField, FileField,
                     TextAreaField, URLField, SelectField, BooleanField)
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length
from ..models import Resource
from wtforms.validators import ValidationError

BODY_TYPES = {
    'LINK': URLField('Enter the Link to the External Resource:',
                     validators=[DataRequired(), Length(1, 255)]),
    'IMAGE': FileField('Choose the Image You Want to Upload:',
                       validators=[FileRequired(), FileAllowed([
                           'jpeg', 'jpg', 'png', 'gif'],
                           'Resource must be an image!')]),
    'BRIEF': TextAreaField('What do You Want to Share with Others?',
                           validators=[DataRequired(), Length(1, 1800)
                                       ], render_kw={'rows': '8'}),
    'COURSE': TextAreaField('Enter Course Description:',
                            validators=[DataRequired(), Length(1, 1800)
                                        ], render_kw={'rows': '4'})
}


class BodyFieldMixin:
    @classmethod
    def create(cls):
        body_type = request.args.get('type', 'LINK')
        cls.body = BODY_TYPES.get(body_type)

        form = cls(request.form)
        if body_type in ['BRIEF', 'COURSE']:
            form.body.description = 'Feel free to use Markdown'

        return form


class ResourceForm(FlaskForm, BodyFieldMixin):
    """This is the form for creating resources of different types."""

    # form fields
    title = StringField('Enter a Title for This Resource:', validators=[
        DataRequired(), Length(1, 255)
    ])
    rtype = SelectField('Resource Type:', choices=[
        (t, name) for t, name in enumerate(Resource.supported_types())
    ], coerce=int)
    published = BooleanField('Publish this resource', default=True)
    submit = SubmitField('Post Resource')

    def __init__(self, *args, **kwargs):
        r_type = request.args.get('type', 'LINK')
        
        super().__init__(*args, **kwargs)
        self.rtype.data = Resource.supported_types().get(r_type).value
        self.rtype.render_kw = {'disabled': True}
    
    def validate_title(self, field):
        resource = Resource.find_by(title=field.data, one=True)
        if resource:
            raise ValidationError('A resource with this title already exists.')
