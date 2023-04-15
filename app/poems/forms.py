from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField,
                     BooleanField, SubmitField,
                     SelectField, TextAreaField)
from wtforms.validators import (DataRequired, Length,
                                NumberRange, Regexp)
from ..models import Category


class PoemForm(FlaskForm):
    """Represents the form for creating or editing poems."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the category choices
        self.category.choices = Category.get_choices()

    title = StringField('New Poem Title',
                        validators=[DataRequired(), Length(1, 255)])
    description = TextAreaField('Describe the New Poem',
                                validators=[Length(0, 3000),],
                                render_kw={'rows': '5'})
    category = SelectField('Select Poem Category', coerce=str,
                           validators=[DataRequired()],)
    is_premium = BooleanField('Is this a premium poem?', name='premium')
    submit = SubmitField('Create/Update Poem')


class StanzaForm(FlaskForm):
    """Represents the form for creating or editing stanzas."""

    index = IntegerField('Enter New Stanza Number (relative to the poem)',
                         validators=[DataRequired(), NumberRange(1, 20)], default=1)
    content = TextAreaField('Enter the Stanza Content', validators=[
        DataRequired(), Length(1, 3000)], render_kw={'rows': '10'})
    submit = SubmitField('Add/Update Stanza')


class CategoryForm(FlaskForm):
    """Represents the form for creating or editing categories."""

    name = StringField('New Category Name',
                       validators=[DataRequired(), Length(1, 100),
                                   Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0,
                                          'Category name must have only letters, numbers, or underscores')])
    description = TextAreaField('Describe Briefly the New Category',
                                validators=[Length(0, 1000)], render_kw={'rows': '3'})
    submit = SubmitField('Add Category')


class CommentForm(FlaskForm):
    """Represents the form for creating or editing comments."""

    comment = TextAreaField('What is your feedback on the poem?', validators=[
        Length(0, 1000), ], render_kw={'rows': '2'})
    submit = SubmitField('Post Comment')
