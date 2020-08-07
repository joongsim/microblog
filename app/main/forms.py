from flask import request
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username', validators=[DataRequired()]))
    password = PasswordField(_l('Password', validators=[DataRequired()]))
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username', validators=[DataRequired()]))
    email = StringField(_l('Email', validators=[DataRequired(), Email()]))
    password = PasswordField(_l('Password', validators=[DataRequired()]))
    password2 = PasswordField(_l(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]))
    submit = SubmitField(_l('Register'))

    # Custom validators validate_<field_name>() are invoked along with stock
    # validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('This username is already taken'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('This email is already registered'))


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username', validators=[DataRequired()]))
    about_me = TextAreaField(_l('About me', validators=[Length(min=0, max=140)]))
    submit = SubmitField(_l('Submit'))

    # Invokes FlaskForm parent class constructor
    # Good practice to override method in both derived and parent classes
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something:', validators=[
        DataRequired(), Length(min=1, max=140)
    ]))
    submit = SubmitField(_l('Submit'))


# Empty form with only a submit button
# Used for follow/unfollow functionality with CSRF protection
class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email', validators=[DataRequired(), Email()]))
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password', validators=[DataRequired()]))
    password2 = _l(PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]))
    submit = _l(SubmitField('Request Password Reset'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        # Flask writes form values for POST requests to request.form
        # and GET requests to request.arg
        # Tells Python where to look to get form submissions
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        # CSRF protection needs to be off for search results to be clickable
        # Tells Flask-WTF to bypass csrf protection for this form
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
