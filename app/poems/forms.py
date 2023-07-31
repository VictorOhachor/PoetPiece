from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField,
                     BooleanField, SubmitField,
                     SelectField, TextAreaField, IntegerRangeField)
from wtforms.validators import (DataRequired, Length,
                                NumberRange, Regexp)
from ..models import Category, Poet
from flask import request


class PoemForm(FlaskForm):
    """Represents the form for creating or editing poems."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the category choices
        self.category.choices = Category.get_choices()

    title = StringField('New Poem Title',
                        validators=[DataRequired(), Length(1, 255)])
    description = TextAreaField('Describe the New Poem (optional)',
                                validators=[Length(0, 3000),],
                                render_kw={'rows': '5'})
    category = SelectField('Select Poem Category', coerce=str,
                           validators=[DataRequired()])
    premium = BooleanField('Mark as Premium')
    submit = SubmitField('Create/Update Poem')


class FilterPoemForm(FlaskForm):
    """Represents the filter form for searching through poems."""

    poet = SelectField('Filter by Poets:',)
    rating = SelectField('Choose Ratings:', choices=[
        ('', 'All'), (1, 'Rating <= 1.0'), (3, '1.0 < Rating <= 3.0'),
        (5, '3.0 < Rating <= 5.0')
    ])
    completed = SelectField('Select Poem State:', choices=[
        (False, 'In Progress'), (True, 'Completed')
    ])
    premium = SelectField('Select Poem Type:', choices=[
        (False, 'Free'), (True, 'Premium')
    ])
    filter_poem = SubmitField('Apply Filters')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the poets choices
        self.poet.choices = [('', 'All'), *Poet.get_choices()]

        # delete csrf token on GET requests
        if request.method == 'GET':
            del self.csrf_token

    def hidden_tag(self, *fields):
        if request.method == 'GET':
            return ''
        return super().hidden_tag(*fields)


class StanzaForm(FlaskForm):
    """Represents the form for creating or editing stanzas."""

    index = IntegerField('Enter New Stanza Number (relative to the poem)',
                         validators=[DataRequired(), NumberRange(1, 20)],
                         default=1)
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
                                validators=[Length(0, 255)],
                                render_kw={'rows': '3'})
    submit = SubmitField('Add Category')


class CommentForm(FlaskForm):
    """Represents the form for creating or editing comments."""

    comment = TextAreaField('Add a comment', validators=[
        Length(1, 1000), DataRequired()], render_kw={'rows': '2'})
    submit = SubmitField('Post')
