from flask_wtf import FlaskForm
from wtforms import (StringField,
                     BooleanField, SubmitField,
                     SelectField, TextAreaField)
from wtforms.validators import (DataRequired, Length, Email)


class CreatePoemForm(FlaskForm):
    """Represents the login form for users/admins."""

    title = StringField('New Poem Title',
                        validators=[DataRequired(), Length(1, 255)])
    description = TextAreaField('Describe the New Poem', validators=[
        DataRequired(), Length(1, 600), ])
    category = SelectField('Select Poem Category', coerce=str, validators=[DataRequired()])
    is_premium = BooleanField('Is this a premium poem?')
    submit = SubmitField('Create Poem')
