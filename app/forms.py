from flask_wtf import FlaskForm
import math
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Optional, NumberRange, Length, EqualTo, ValidationError
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

def finite_coordinate(form, field):
    if field.data is not None and not math.isfinite(field.data):
        raise ValidationError('Enter a finite coordinate.')


class CoordinateForm(FlaskForm):
    latitude = FloatField('Latitude (Optional)', validators=[
        Optional(), finite_coordinate, NumberRange(min=-90, max=90),
    ])
    longitude = FloatField('Longitude (Optional)', validators=[
        Optional(), finite_coordinate, NumberRange(min=-180, max=180),
    ])

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)
        if not self.latitude.errors and not self.longitude.errors:
            if (self.latitude.data is None) != (self.longitude.data is None):
                missing = self.latitude if self.latitude.data is None else self.longitude
                missing.errors.append('Enter both latitude and longitude, or leave both blank.')
                valid = False
        return valid


class PropertyForm(CoordinateForm):
    name = StringField('Property Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Property')

class StandForm(CoordinateForm):
    name = StringField('Stand Name', validators=[DataRequired(), Length(max=100)])
    degree = IntegerField('Facing direction (0-360)', validators=[InputRequired(), NumberRange(min=0, max=360)])
    submit = SubmitField('Save Stand')


class DeleteStandForm(FlaskForm):
    submit = SubmitField('Delete Stand')


class DeletePropertyForm(FlaskForm):
    submit = SubmitField('Delete Property')


class DeleteAccountForm(FlaskForm):
    submit = SubmitField('Delete Account')

