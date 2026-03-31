from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User
from app.field_mappings import FIELD_CHOICES, WIZARD_STEPS


class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters.')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class PredictionForm(FlaskForm):
    """Dynamic prediction form with all 25 fields as dropdowns/inputs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set choices for all select fields
        for step in WIZARD_STEPS:
            for field_name in step['fields']:
                field_info = FIELD_CHOICES[field_name]
                if hasattr(self, field_name) and field_info['choices']:
                    getattr(self, field_name).choices = field_info['choices']

    # Step 1: Policy Information
    PolicyNumber = StringField('Policy Number', validators=[DataRequired(), Length(min=1, max=50)])
    WeekOfMonth = SelectField('Week of Month', validators=[DataRequired()])
    PolicyType = SelectField('Policy Type', validators=[DataRequired()])
    BasePolicy = SelectField('Base Policy', validators=[DataRequired()])
    Deductible = SelectField('Deductible Amount', validators=[DataRequired()])
    Days_Policy_Accident = SelectField('Days: Policy to Accident', validators=[DataRequired()])
    Days_Policy_Claim = SelectField('Days: Policy to Claim', validators=[DataRequired()])
    AgentType = SelectField('Agent Type', validators=[DataRequired()])

    # Step 2: Personal Information
    Sex = SelectField('Gender', validators=[DataRequired()])
    MaritalStatus = SelectField('Marital Status', validators=[DataRequired()])
    Age = FloatField('Age', validators=[DataRequired(), NumberRange(min=16, max=100, message='Age must be between 16 and 100.')])
    AgeOfPolicyHolder = SelectField('Age Group of Policy Holder', validators=[DataRequired()])
    Fault = SelectField('Fault Attribution', validators=[DataRequired()])
    PastNumberOfClaims = SelectField('Past Number of Claims', validators=[DataRequired()])
    AddressChange_Claim = SelectField('Address Change Since Claim', validators=[DataRequired()])

    # Step 3: Vehicle & Accident
    Make = SelectField('Vehicle Manufacturer', validators=[DataRequired()])
    VehicleCategory = SelectField('Vehicle Category', validators=[DataRequired()])
    VehiclePrice = SelectField('Vehicle Price Range', validators=[DataRequired()])
    AgeOfVehicle = SelectField('Age of Vehicle', validators=[DataRequired()])
    AccidentArea = SelectField('Accident Area', validators=[DataRequired()])
    NumberOfCars = SelectField('Number of Cars', validators=[DataRequired()])

    # Step 4: Claim Details
    DayOfWeekClaimed = SelectField('Day of Week Claimed', validators=[DataRequired()])
    WeekOfMonthClaimed = SelectField('Week of Month Claimed', validators=[DataRequired()])
    PoliceReportFiled = SelectField('Police Report Filed', validators=[DataRequired()])
    WitnessPresent = SelectField('Witness Present', validators=[DataRequired()])
    NumberOfSuppliments = SelectField('Number of Supplements', validators=[DataRequired()])

    submit = SubmitField('Analyze Claim')
