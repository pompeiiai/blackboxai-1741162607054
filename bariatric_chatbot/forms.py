from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=64)
    ])
    phone = StringField('Phone', validators=[Length(max=20)])
    roles = SelectMultipleField('Roles', coerce=int)

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class EditUserForm(UserForm):
    password = PasswordField('Password', validators=[
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email.')

class AppointmentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    scheduled_time = DateTimeField('Date & Time', validators=[DataRequired()])
    appointment_type = SelectField('Type', validators=[DataRequired()], choices=[
        ('consultation', 'Initial Consultation'),
        ('followup', 'Follow-up'),
        ('preop', 'Pre-operative'),
        ('postop', 'Post-operative')
    ])
    status = SelectField('Status', validators=[DataRequired()], choices=[
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    notes = TextAreaField('Notes')

class ChatConfigForm(FlaskForm):
    surgery_type = StringField('Surgery Type', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    cost_min = StringField('Minimum Cost', validators=[DataRequired()])
    cost_max = StringField('Maximum Cost', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    risks = TextAreaField('Risks', validators=[DataRequired()])
    recovery_time = StringField('Recovery Time', validators=[DataRequired()])

class DietPlanForm(FlaskForm):
    surgery_type_id = SelectField('Surgery Type', coerce=int, validators=[DataRequired()])
    phase = StringField('Phase', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    allowed_foods = TextAreaField('Allowed Foods', validators=[DataRequired()])
    restricted_foods = TextAreaField('Restricted Foods', validators=[DataRequired()])
    guidelines = TextAreaField('Guidelines', validators=[DataRequired()])
    supplements = TextAreaField('Supplements', validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    filter_by = SelectField('Filter By', choices=[
        ('all', 'All'),
        ('users', 'Users'),
        ('appointments', 'Appointments'),
        ('chat_history', 'Chat History')
    ])
