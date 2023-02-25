from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                     BooleanField, SubmitField,
                     DateField, SelectField)
from wtforms.validators import (DataRequired, Length, Optional,
                                Regexp, EqualTo, Email, AnyOf,
                                InputRequired)
from wtforms import ValidationError
from ..models import User, Admin


class LoginForm(FlaskForm):
    """Represents the login form for users/admins."""

    username = StringField('Remind Me Your Username', validators=[
        InputRequired('Username Required!'), DataRequired(), Length(3, 100)
    ])
    password = PasswordField('How About Your Password?', validators=[
        InputRequired('Password Required!'), DataRequired(),
    ])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class SignupForm(FlaskForm):
    """Represents the login form for users."""

    username = StringField('What Would You Like Me To Call You? (Username)', validators=[
        DataRequired(), Length(3, 100),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Enter a New Password', validators=[
        DataRequired(), Length(8, 128, 'Number of characters must be between 8 and 128'),
    ])
    password2 = PasswordField('Confirm New Password',
                              validators=[
                                  DataRequired(),
                                  EqualTo('password',
                                          message='Passwords must match.')
                              ])
    birth_date = DateField('Enter Your Date of Birth',
                           validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        """Ensure that the username passed does not already exists."""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already in use.')


class AdminSignupForm(FlaskForm):
    """Represent the form for users to become a poet."""

    email = StringField('Register Your Email with Us',
                        validators=[DataRequired(), Length(1, 255), Email()])
    gender = SelectField('Select Your Gender',
                         choices=[('', '-- Select an option --'), ('female', 'Female'),
                                  ('male', 'Male'), ('others', 'Others')
                                  ], coerce=str, validators=[
                             DataRequired(), AnyOf(
                                 ['female', 'male', 'others'])
                         ])
    password = PasswordField('Enter Your Password to Confirm your Identity', validators=[
        DataRequired(),
    ])
    submit = SubmitField('Create Poet Account')

    def validate_email(self, field):
        """Ensure the email passed does not already exists."""
        admin = Admin.query.filter_by(email=field.data).first()
        if admin:
            raise ValidationError('Email already registered.')

    def validate_password(self, field):
        """Ensure that password is correct."""
        user = User.query.filter_by(username=current_user.username).first()
        if not user:
            raise ValidationError('You are not a registered user.')

        if not user.verify_password(field.data):
            raise ValidationError("Your password is incorrect.")

    def validate_gender(self, field):
        """Ensure that gender is male, female, or others."""
        if field.data.lower() not in ['male', 'female', 'others']:
            raise ValidationError('Gender must be male, female, or others.')


class EditProfileForm(FlaskForm):
    """Represent the updation form for a user/admin profile."""

    username = StringField('Update Your Username (optional): ', validators=[
        Optional(), Length(3, 100),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or underscores')])
    gender = SelectField('Update Your Gender (optional): ',
                         choices=[('', '-- Select an option --'), ('female', 'Female'),
                                  ('male', 'Male'), ('others', 'Others')
                                  ], coerce=str, validators=[
                             Optional(), AnyOf(
                                 ['female', 'male', 'others'])
                         ])
    birth_date = DateField(
        'Update Your Date of Birth (optional): ', validators=[Optional()])
    submit = SubmitField('Update Profile')


class UpdatePasswordForm(FlaskForm):
    """Update user's password."""

    old_password = PasswordField(
        'Enter Old Password:', validators=[DataRequired(),])
    new_password = PasswordField('Enter a New Password:', validators=[
        DataRequired(), Length(8, 128,
                               'Number of characters must be between 8 and 128')
    ])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[
                                         DataRequired(),
                                         EqualTo('new_password',
                                                 message='Passwords must match.')
                                     ])
    submit = SubmitField('Update Password')

    def validate_old_password(self, field):
        """Ensure that old password is correct."""
        user = User.query.get(current_user.id)

        if not user.verify_password(field.data):
            raise ValidationError('You provided an incorrect password!')
