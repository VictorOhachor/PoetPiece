from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp


class AddCategoryForm(FlaskForm):
    """Represents the login form for users/admins."""

    name = StringField('New Category Name',
                       validators=[DataRequired(), Length(1, 100),
                       Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0,
               'Category name must have only letters, numbers, or underscores')])
    description = TextAreaField('Describe Briefly the New Category', validators=[
        DataRequired(), Length(1, 1000)])
    submit = SubmitField('Add Category')
