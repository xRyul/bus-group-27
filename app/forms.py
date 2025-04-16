import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FileField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app import db
from app.models.user import User


class ChooseForm(FlaskForm):
    choice = HiddenField("Choice")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


activity_choices = [
    "Cycled to Campus",
    "Used public transport",
    "Recycled materials",
    "Used Reusable Container",
    "Attended Sustainability Event",
    "Reported Energy Waste",
    "Reported Water Waste",
    "Used an e-scooter",
]


class UserSubmission(FlaskForm):
    activity_type = SelectField(
        "Activity Type", choices=activity_choices, validators=[DataRequired()]
    )
    description = TextAreaField("Description")
    evidence = FileField("Upload Evidence")
    upload = SubmitField("Upload")
