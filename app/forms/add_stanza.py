from flask_wtf import FlaskForm
from wtforms import (IntegerField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Length, NumberRange)


class AddStanzaForm(FlaskForm):
    """Represents the login form for users/admins."""

    index = IntegerField('Enter New Stanza Number (relative to the poem)',
                       validators=[DataRequired(), NumberRange(1, 20)], default=1)
    content = TextAreaField('Enter the Stanza Content', validators=[
        DataRequired(), Length(1, 3000)])
    submit = SubmitField('Add Stanza')
