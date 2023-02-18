from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                     BooleanField, SubmitField)
from wtforms.validators import DataRequired, Length, InputRequired


class LoginForm(FlaskForm):
    """Represents the login form for users/admins."""

    username = StringField('Remind Me Your Username', validators=[
        InputRequired('Username Required!'), DataRequired(), Length(3, 100)
    ])
    password = PasswordField('How About Your Password?', validators=[
        InputRequired('Password Required!'), DataRequired(),
        Length(8, 128, 'Number of characters must be between 8 and 128')
    ])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
