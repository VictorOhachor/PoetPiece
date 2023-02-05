from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Length)


class AddCategoryForm(FlaskForm):
    """Represents the login form for users/admins."""

    name = StringField('New Category Name',
                       validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Describe Briefly the New Category', validators=[
        DataRequired(), Length(1, 1000)])
    submit = SubmitField('Add Category')
