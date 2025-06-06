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
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired

from app.debug_utils import activity_types


class ChooseForm(FlaskForm):
    choice = HiddenField("Choice")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


# Convert activity_types dictionary defined in debug_utils.py to a list of tuples for the form
activity_choices = [(code, info["name"]) for code, info in activity_types.items()]


class UserSubmission(FlaskForm):
    activity_type = SelectField(
        "Activity Type", choices=activity_choices, validators=[DataRequired()]
    )
    description = TextAreaField("Description")
    evidence = FileField("Upload Evidence")
    submit = SubmitField("Submit")
