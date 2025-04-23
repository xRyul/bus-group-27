from dataclasses import dataclass
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from app.models.sustainable_activity import (
    SustainableActivity,  # For the 'activities' relationship
)
from app.models.user_points import UserPoints  # For the 'points' relationship


@dataclass
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[str] = so.mapped_column(sa.String(10), default="Normal")

    # One-to-many relationship: A single user can have multiple sustainable activities.
    # The foreign key is defined in the SustainableActivity model (user_id field)
    # This relationship allows querying all activities associated with a user, e.g., user.activities.all()
    activities: so.WriteOnlyMapped["SustainableActivity"] = so.relationship(
        back_populates="user", lazy="dynamic"
    )

    # One-to-one relationship: A single user can have only one set of points.
    # The foreign key is defined in the UserPoints model (user_id field)
    # This relationship allows accessing a user's points directly, e.g., user.points
    points: so.Mapped[Optional["UserPoints"]] = (
        so.relationship(  # User might not have points yet
            back_populates="user", uselist=False
        )
    )

    def __repr__(self):
        pwh = "None" if not self.password_hash else f"...{self.password_hash[-5:]}"
        return f"User(id={self.id}, username={self.username}, email={self.email}, role={self.role}, pwh={pwh})"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
