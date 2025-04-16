from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined

from config import Config

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "login"

from app import models, views
from app.debug_utils import reset_db


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, sa=sa, so=so, reset_db=reset_db)


@app.context_processor
def inject_current_year():
    year = datetime.now().year
    print(f"Injecting current year: {year}")
    return {"current_year": year}
