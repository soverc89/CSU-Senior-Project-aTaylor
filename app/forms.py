from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PropertyForm(FlaskForm):
    name = StringField('Property Name', validators=[DataRequired(), Length(max=100)])
    latitude = StringField('Latitude (Optional)')
    longitude = StringField('Longitude (Optional)')
    submit = SubmitField('Save Property')

class StandForm(FlaskForm):
    name = StringField('Stand Name', validators=[DataRequired(), Length(max=100)])
    degree = StringField('Degree Direction (0-360)', validators=[DataRequired()])
    submit = SubmitField('Save Stand')

