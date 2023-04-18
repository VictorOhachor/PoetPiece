from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                     BooleanField, SubmitField,
                     DateField, SelectField, TextAreaField)
from wtforms.validators import (DataRequired, Length,
                                Regexp, EqualTo, Email, AnyOf)
from wtforms import ValidationError
from ..models import User, Poet


def _username_field(label):
    return StringField(label, validators=[
        DataRequired(), Length(3, 100),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or underscores')])


def _password_field(label, *validators):
    return PasswordField(label, validators=[
        DataRequired('Password Required!'),
        Length(8, 128, 'Number of characters must be between 8 and 128'),
        *validators
    ])


class LoginForm(FlaskForm):
    """Represents the login form for users."""

    username = _username_field('Remind Me Your Username:')
    password = _password_field('How About Your Password?:')
    remember_me = BooleanField('Stay logged in')
    submit = SubmitField('Hop in, fella!')


class SignupForm(FlaskForm):
    """Represents the login form for users."""

    username = _username_field('Choose a New Username:')
    password = _password_field('Enter a New Password:')
    password2 = _password_field('Confirm New Password:',
                                EqualTo('password', message='Passwords must match.'))
    birth_date = DateField('Enter Your Date of Birth:',
                           validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        """Ensure that the username passed does not already exists."""
        user = User.find_by(username=field.data, one=True)
        if user:
            raise ValidationError('Username already in use.')


class PoetForm(FlaskForm):
    """Represent the form for users to become a poet."""

    email = StringField('Register Your Email With Us:',
                        validators=[DataRequired(), Length(1, 255), Email()])
    gender = SelectField('Select Your Gender',
                         choices=[('', '-- Select an option --'), ('female', 'Female'),
                                  ('male', 'Male'), ('others', 'Others')
                                  ], coerce=str, validators=[
                             DataRequired(), AnyOf(
                                 ['female', 'male', 'others'])
                         ])
    bio = TextAreaField('Enter a brief bio about yourself:', validators=[
        DataRequired(), Length(1, 2000)
    ])
    password = _password_field('Enter Your Password to Confirm your Identity')
    submit = SubmitField('Submit')

    def validate_email(self, field):
        """Ensure the email passed does not already exists."""
        poet = Poet.find_by(email=field.data, one=True)
        if poet:
            raise ValidationError('Email already registered.')

    def validate_password(self, field):
        """Ensure that password is correct."""
        user = User.find_by(username=current_user.username, one=True)
        if not user:
            raise ValidationError('You are not a registered user.')

        if not user.verify_password(field.data):
            raise ValidationError("Your password is incorrect.")


class EditProfileForm(FlaskForm):
    """Represent the updation form for a user profile."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not current_user.is_poet:
            del self.gender
            del self.email

    email = StringField('Update Your Email Address:',
                        validators=[DataRequired(), Length(1, 255), Email()])
    username = _username_field('Update Your Username: ')
    gender = SelectField('Update Your Gender: ',
                         choices=[('', '--- Choose your gender ---'), ('female', 'Female'),
                                  ('male', 'Male'), ('others', 'Others')], coerce=str,
                         validators=[DataRequired(), AnyOf(
                             ['female', 'male', 'others'])
                         ])
    bio = TextAreaField('Enter a brief bio about yourself:', validators=[
        DataRequired(), Length(1, 2000)])
    birth_date = DateField('Update Your Date of Birth (optional): ',
                           validators=[DataRequired()])
    submit = SubmitField('Update Profile')


class UpdatePasswordForm(FlaskForm):
    """ Update user's password. """

    old_password = _password_field('Enter Old Password:')
    password = _password_field('Enter a New Password:')
    confirm_password = _password_field('Confirm New Password',
                                       EqualTo('password', message='Passwords must match.'))
    submit = SubmitField('Update Password')

    def validate_old_password(self, field):
        """Ensure that old password is correct."""
        user = User.query.get(current_user.id)

        if not user.verify_password(field.data):
            raise ValidationError('You provided an incorrect password!')
