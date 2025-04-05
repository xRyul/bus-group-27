from app import db
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import ForeignKey
from dataclasses import dataclass

@dataclass
class SustainableActivity(db.Model):
    __tablename__ = 'sustainable_activities'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(ForeignKey('users.id'))
    activity_type: so.Mapped[str] = so.mapped_column(sa.String(50))
    description: so.Mapped[str] = so.mapped_column(sa.String(255))
    timestamp: so.Mapped[datetime.datetime] = so.mapped_column(sa.DateTime, default=datetime.datetime.utcnow)
    evidence: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=True)
    status: so.Mapped[str] = so.mapped_column(sa.String(20), default='pending')  # pending, verified, rejected
    points_awarded: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    carbon_saved: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    
    # Relationship: many-to-one with User
    user = db.relationship('User', back_populates='activities')
    
    def __repr__(self):
        return f'SustainableActivity(id={self.id}, user_id={self.user_id}, activity_type={self.activity_type}, status={self.status}, points={self.points_awarded})'