from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models_mongo import User  # Changed from models to models_mongo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember Me')
