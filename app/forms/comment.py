from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import (DataRequired, Length)


class CreateCommentForm(FlaskForm):
    """Represents the login form for users/admins."""

    comment = TextAreaField('What is your feedback on the poem?', validators=[
        DataRequired(), Length(1, 1000), ])
    submit = SubmitField('Comment')
