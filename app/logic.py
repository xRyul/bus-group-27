import sqlalchemy as sa
from sqlalchemy import func, extract
from app import db
from app.models.building import Building
from app.models.building_energy import BuildingEnergy
from app.models.sustainable_activity import SustainableActivity
from app.models.user import User
from app.models.user_points import UserPoints


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class BuildingEnergyMonitoring(metaclass=SingletonMeta):
    def __init__(self):
        # Simulated DATA is generated in the debug_utils.py
        pass

    # Return all buildings ordered by name
    def get_all_buildings(self):
        return db.session.scalars(sa.select(Building).order_by(Building.name)).all()

    # Find the most appropriate default building ID from a list of buildings
    def get_default_building_id(self, buildings):
        if not buildings:
            return None
            
        # Try to find Computer Science building first
        cs_building = next((b for b in buildings if b.name == "Computer Science"), None)
        if cs_building:
            return cs_building.id
        
        # Fall back to first building in the list
        return buildings[0].id

    # Validate a selected building ID and return a valid ID
    def validate_building_selection(self, selected_id, buildings):
        if not buildings:
            return None
            
        valid_building_ids = {b.id for b in buildings}
        if selected_id in valid_building_ids:
            return selected_id
        
        # Not valid - get default instead
        return self.get_default_building_id(buildings)
    
    # Get hourly average energy consumption for a building and energy type
    def get_hourly_average(self, energy_type, building_id):
        avg_data = db.session.query(
            extract('hour', BuildingEnergy.timestamp).label('hour'),
            func.avg(BuildingEnergy.consumption_value).label('average_consumption')
            ).filter(
                BuildingEnergy.building_id == building_id,
                BuildingEnergy.energy_type == energy_type
            ).group_by(extract('hour', BuildingEnergy.timestamp)
            ).order_by(extract('hour', BuildingEnergy.timestamp)
            ).all()
        # Ensure all 24 hours are present, default to 0
        data_dict = {hour: avg for hour, avg in avg_data}
        return [data_dict.get(h, 0) for h in range(24)]

    # Get anomalies for a specific building across all energy types
    def get_anomalies_for_building(self, building_id):
        anomaly_records = db.session.query(
            BuildingEnergy.timestamp,
            BuildingEnergy.consumption_value,
            BuildingEnergy.energy_type
        ).filter(
            BuildingEnergy.building_id == building_id,
            BuildingEnergy.energy_type.in_(['electric', 'gas', 'water']),
            BuildingEnergy.is_anomaly.is_(True)
        ).order_by(
            BuildingEnergy.timestamp, BuildingEnergy.energy_type
        ).all()

        # Anomalies dictionary, keyed by energy type
        anomalies_by_type = {'electric': [], 'gas': [], 'water': []}
        for timestamp, value, energy_type in anomaly_records:
            if energy_type in anomalies_by_type:
                hour_index = timestamp.hour
                anomalies_by_type[energy_type].append({"index": hour_index, "value": value})
                
        return anomalies_by_type

    # Get total count of anomalies across all energy types
    def get_anomaly_count(self, anomalies_by_type):
        return sum(len(v) for v in anomalies_by_type.values())

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
    
    # FR6 logic
    def award_points(self, activity: SustainableActivity):
        if activity.points_awarded is not None:
            return {"error": "Points have already been awarded for this activity."}, 400
    
        # Award 10 points per kg CO2 saved
        points_awarded = activity.carbon_saved * 10
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
            "message": f"Awarded {points_awarded} points for {activity.activity_type}",
            "total_points": self.user.points.total_points
        }, 200