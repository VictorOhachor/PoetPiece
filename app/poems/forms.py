from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField,
                     BooleanField, SubmitField,
                     SelectField, TextAreaField)
from wtforms.validators import (DataRequired, Length,
                                NumberRange, Regexp)


class CreatePoemForm(FlaskForm):
    """Represents the login form for users/admins."""

    title = StringField('New Poem Title',
                        validators=[DataRequired(), Length(1, 255)])
    description = TextAreaField('Describe the New Poem',
                                validators=[Length(0, 600), ],
                                render_kw={'rows': '10'})
    category = SelectField('Select Poem Category',
                           coerce=str, validators=[DataRequired()])
    is_premium = BooleanField('Is this a premium poem?')
    submit = SubmitField('Create/Update Poem')


class StanzaForm(FlaskForm):
    """Represents the login form for users/admins."""

    index = IntegerField('Enter New Stanza Number (relative to the poem)',
                         validators=[DataRequired(), NumberRange(1, 20)], default=1)
    content = TextAreaField('Enter the Stanza Content', validators=[
        DataRequired(), Length(1, 3000)], render_kw={'rows': '20'})
    submit = SubmitField('Add/Update Stanza')


class AddCategoryForm(FlaskForm):
    """Represents the login form for users/admins."""

    name = StringField('New Category Name',
                       validators=[DataRequired(), Length(1, 100),
                                   Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0,
                                          'Category name must have only letters, numbers, or underscores')])
    description = TextAreaField('Describe Briefly the New Category', validators=[
        DataRequired(), Length(1, 1000)], render_kw={'rows': '5'})
    submit = SubmitField('Add Category')


class CreateCommentForm(FlaskForm):
    """Represents the login form for users/admins."""

    comment = TextAreaField('What is your feedback on the poem?', validators=[
        DataRequired(), Length(1, 1000), ])
    submit = SubmitField('Post Comment')
