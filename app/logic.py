import numpy as np
from app.models.user import User
from app.models.sustainable_activity import SustainableActivity
from app.models.user_points import UserPoints
from app import db
from datetime import datetime, timedelta
from app.models.building_energy import BuildingEnergy
from app.models.building import Building
import random
from collections import defaultdict

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class BuildingEnergyMonitoring(metaclass=SingletonMeta):
    def __init__(self):
        self.raw_data = []
        self.processed_data = []
        self.anomaly_lookup = set()

        self.simulate_midweek_energy_readings({
            "Computer Science": 1,
            "Physics": 2,
            "Library": 3
        })
        self.inject_known_anomalies()
        self.detect_anomalies_iqr()
        self.create_model_objects()
        self.commit_to_database()

    def simulate_midweek_energy_readings(self, building_name_to_id):
        buildings = ["Computer Science", "Physics", "Library"]
        energy_types = {
            "electric": ("kWh", 80, 160),
            "water": ("litres", 150, 250),
            "gas": ("m3", 2.5, 4.5)
        }

        start_day = datetime(2025, 4, 11)
        intervals_per_day = 96

        for building in buildings:
            building_id = building_name_to_id[building]
            for energy_type, (unit, low, high) in energy_types.items():
                for interval in range(intervals_per_day):
                    timestamp = start_day + timedelta(minutes=15 * interval)
                    hour = timestamp.hour
                    base = {
                        "electric": 100 if 8 <= hour <= 18 else 60,
                        "water": 200 if 7 <= hour <= 20 else 150,
                        "gas": 3.5 if 6 <= hour <= 22 else 2.5
                    }[energy_type]
                    noise = random.uniform(-3, 3)
                    value = round(base + noise, 2)
                    self.raw_data.append((building_id, timestamp, energy_type, value, unit))

    def inject_known_anomalies(self):
        updated = []
        for (building_id, timestamp, energy_type, value, unit) in self.raw_data:
            if (
                (timestamp.hour == 8 and timestamp.minute == 0 and energy_type == "electric") or
                (timestamp.hour == 14 and energy_type == "water") or
                (timestamp.hour == 20 and energy_type == "gas")
            ):
                value = round(value + 75.0, 2)
            updated.append((building_id, timestamp, energy_type, value, unit))
        self.raw_data = updated

    def detect_anomalies_iqr(self, k=1.5):
        grouped = defaultdict(lambda: defaultdict(list))
        timestamps = defaultdict(lambda: defaultdict(list))

        for building_id, timestamp, energy_type, value, unit in self.raw_data:
            grouped[building_id][energy_type].append(value)
            timestamps[building_id][energy_type].append(timestamp)

        for building_id, utilities in grouped.items():
            for energy_type, values in utilities.items():
                values_array = np.array(values)
                q1 = np.percentile(values_array, 25)
                q3 = np.percentile(values_array, 75)
                iqr = q3 - q1
                lower = q1 - k * iqr
                upper = q3 + k * iqr

                for i, val in enumerate(values):
                    if val < lower or val > upper:
                        ts = timestamps[building_id][energy_type][i]
                        self.anomaly_lookup.add((building_id, energy_type, ts))

    def create_model_objects(self):
        for building_id, timestamp, energy_type, value, unit in self.raw_data:
            is_anomaly = (building_id, energy_type, timestamp) in self.anomaly_lookup
            model_instance = BuildingEnergy(
                building_id=building_id,
                timestamp=timestamp,
                energy_type=energy_type,
                consumption_value=value,
                unit=unit,
                is_anomaly=is_anomaly
            )
            self.processed_data.append(model_instance)

    def commit_to_database(self):
        db.session.add_all(self.processed_data)
        db.session.commit()

# BuildingEnergyMonitoring = BuildingEnergyMonitoring()
# print(BuildingEnergyMonitoring.processed_data)

class CommunityEngagement:
    ### FR5 Logic ###
    def __init__(self, user: User):
        self.user = user

    def log_activity(self, activity: SustainableActivity):
        if not self.user or not activity:
            return {'error': 'Invalid user or activity'}, 400

        user_activity = SustainableActivity(
            user_id=self.user.id,
            activity_type=activity.activity_type,
            description=activity.description,
            points_awarded=activity.points_awarded,
            carbon_saved=activity.carbon_saved,
            status='verified'
        )
        db.session.add(user_activity)
        self._update_user_points(activity)
        db.session.commit()

        return {
            'message': f"Activity logged. {activity.points_awarded} points awarded.",
            'total_points': self.user.points.total_points
        }, 200

    def submit_activity(self, activity_type: str, description: str = "", evidence: str = None):
        try:
            activity = SustainableActivity(
                user_id=self.user.id,
                activity_type=activity_type,
                description=description,
                evidence=evidence,
                status='pending'
            )
            db.session.add(activity)
            db.session.commit()
            return {"message": "Activity submitted for review."}, 201
        except Exception as e:
            return {"error": str(e)}, 400

    def _update_user_points(self, activity: SustainableActivity):
        if hasattr(self.user, 'points') and self.user.points:
            self.user.points.total_points += activity.points_awarded
            self.user.points.green_score += activity.carbon_saved
        else:
            self.user.points = UserPoints(
                total_points=activity.points_awarded,
                green_score=activity.carbon_saved,
                user_id=self.user.id
            )
            db.session.add(self.user.points)
    
    ### FR6 Logic ###
    def award_points(self, activity: SustainableActivity):
        if activity.status != 'verified':
            return {"error": "Activity must be verified to award points."}, 400

        points_awarded = self.calculate_points(activity.carbon_saved)
        activity.points_awarded = points_awarded

        if hasattr(self.user, 'points'):
            self.user.points.total_points += points_awarded
            self.user.points.green_score += activity.carbon_saved
        else:
            self.user.points = UserPoints(
                total_points=points_awarded,
                green_score=activity.carbon_saved,
                user_id=self.user.id
            )
            db.session.add(self.user.points)
        db.session.commit()

        return {
            'message': f"{points_awarded} points awarded based on carbon impact.",
            'total_points': self.user.points.total_points,
            'green_score': self.user.points.green_score
        }, 200

    def calculate_points(self, carbon_saved: float) -> int:
        return int(carbon_saved * 2)
