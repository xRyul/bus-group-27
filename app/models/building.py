from app import db
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from dataclasses import dataclass

@dataclass
class Building(db.Model):
    __tablename__ = 'buildings'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100))
    location: so.Mapped[str] = so.mapped_column(sa.String(255))
    total_area: so.Mapped[float] = so.mapped_column(sa.Float)
    energy_class: so.Mapped[str] = so.mapped_column(sa.String(20))
    
    # Relationship: one-to-many with BuildingEnergy
    energy_readings = db.relationship('BuildingEnergy', back_populates='building', lazy='dynamic')
    
    def __repr__(self):
        return f'Building(id={self.id}, name={self.name}, location={self.location}, energy_class={self.energy_class})'