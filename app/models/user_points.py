from app import db
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import ForeignKey
from dataclasses import dataclass

@dataclass
class UserPoints(db.Model):
    __tablename__ = 'user_points'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(ForeignKey('users.id'), unique=True)
    total_points: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    green_score: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    last_updated: so.Mapped[datetime.datetime] = so.mapped_column(sa.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship: one-to-one with User
    user = db.relationship('User', back_populates='points')
    
    def __repr__(self):
        return f'UserPoints(id={self.id}, user_id={self.user_id}, total_points={self.total_points}, green_score={self.green_score}, last_updated={self.last_updated})'
