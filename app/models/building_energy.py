import datetime
from dataclasses import dataclass

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import ForeignKey

from app import db


@dataclass
class BuildingEnergy(db.Model):
    __tablename__ = "building_energy"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    building_id: so.Mapped[int] = so.mapped_column(ForeignKey("buildings.id"))
    timestamp: so.Mapped[datetime.datetime] = so.mapped_column(sa.DateTime, default=datetime.datetime.utcnow)
    energy_type: so.Mapped[str] = so.mapped_column(sa.String(20))  # electricity, gas, water
    consumption_value: so.Mapped[float] = so.mapped_column(sa.Float)
    unit: so.Mapped[str] = so.mapped_column(sa.String(10))  # kWh, m3, etc.
    is_anomaly: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    # Relationship: many-to-one with Building
    building = db.relationship("Building", back_populates="energy_readings")

    def __repr__(self):
        return f"BuildingEnergy(id={self.id}, building_id={self.building_id}, timestamp={self.timestamp}, energy_type={self.energy_type}, value={self.consumption_value} {self.unit}, anomaly={self.is_anomaly})"
