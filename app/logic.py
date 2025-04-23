from typing import Optional

import sqlalchemy as sa
from sqlalchemy import extract, func

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
        avg_data = (
            db.session.query(
                extract("hour", BuildingEnergy.timestamp).label("hour"),
                func.avg(BuildingEnergy.consumption_value).label("average_consumption"),
            )
            .filter(
                BuildingEnergy.building_id == building_id,
                BuildingEnergy.energy_type == energy_type,
            )
            .group_by(extract("hour", BuildingEnergy.timestamp))
            .order_by(extract("hour", BuildingEnergy.timestamp))
            .all()
        )
        # Ensure all 24 hours are present, default to 0
        data_dict = {hour: avg for hour, avg in avg_data}
        return [data_dict.get(h, 0) for h in range(24)]

    # Get anomalies for a specific building across all energy types
    def get_anomalies_for_building(self, building_id):
        anomaly_records = (
            db.session.query(
                BuildingEnergy.timestamp,
                BuildingEnergy.consumption_value,
                BuildingEnergy.energy_type,
            )
            .filter(
                BuildingEnergy.building_id == building_id,
                BuildingEnergy.energy_type.in_(["electric", "gas", "water"]),
                BuildingEnergy.is_anomaly.is_(True),
            )
            .order_by(BuildingEnergy.timestamp, BuildingEnergy.energy_type)
            .all()
        )

        # Anomalies dictionary, keyed by energy type
        anomalies_by_type = {"electric": [], "gas": [], "water": []}
        for timestamp, value, energy_type in anomaly_records:
            if energy_type in anomalies_by_type:
                hour_index = timestamp.hour
                anomalies_by_type[energy_type].append(
                    {"index": hour_index, "value": value}
                )

        return anomalies_by_type

    # Get total count of anomalies across all energy types
    def get_anomaly_count(self, anomalies_by_type):
        return sum(len(v) for v in anomalies_by_type.values())

    # Calculate total energy consumption for a building (electric + gas)
    def calculate_total_consumption(
        self, hourly_data_electric, hourly_data_gas, time_period="day", custom_days=None
    ):
        # The hourly_data already contains the average hourly consumption for each hour
        # We don't need to multiply by 24 again as the values are already per hour

        # Debug: Print hourly data
        print(f"Hourly electric data: {hourly_data_electric}")
        print(f"Hourly gas data: {hourly_data_gas}")

        # Daily consumption - sum of hourly values
        # Each value in hourly_data represents the average consumption for that hour
        # So the daily total is just the sum of all hourly values
        total_electric_daily = sum(hourly_data_electric)
        total_gas_daily = sum(hourly_data_gas)

        print(f"Daily electric total: {total_electric_daily}")
        print(f"Daily gas total: {total_gas_daily}")

        # Scale based on selected time period
        scaling_factors = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
            "custom": custom_days if custom_days is not None else 1,
        }

        scaling = scaling_factors.get(time_period, 1)
        print(f"Time period: {time_period}, Scaling factor: {scaling}")

        total_electric = total_electric_daily * scaling
        total_gas = total_gas_daily * scaling

        print(f"Scaled electric total: {total_electric}")
        print(f"Scaled gas total: {total_gas}")

        # Convert gas (m3) to kWh using approximate conversion factor
        gas_to_kwh = total_gas * 10.55
        print(f"Gas converted to kWh: {gas_to_kwh}")

        # Final total
        final_total = round(total_electric + gas_to_kwh)
        print(f"Final total consumption: {final_total} kWh")

        # Return total in kWh
        return final_total

    # Calculate estimated cost based on consumption
    def calculate_estimated_cost(
        self, hourly_data_electric, hourly_data_gas, time_period="day", custom_days=None
    ):
        # Get total consumption for the time period
        total_electric_daily = sum(hourly_data_electric)
        total_gas_daily = sum(hourly_data_gas)

        # Scale based on selected time period
        scaling_factors = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
            "custom": custom_days if custom_days is not None else 1,
        }

        scaling = scaling_factors.get(time_period, 1)

        total_electric = total_electric_daily * scaling
        total_gas = total_gas_daily * scaling
        gas_to_kwh = total_gas * 10.55

        # Approximate rates: £0.15 per kWh for electricity, £0.05 per kWh for gas
        return round(total_electric * 0.15 + gas_to_kwh * 0.05, 2)

    # Calculate carbon footprint based on consumption
    def calculate_carbon_footprint(
        self, hourly_data_electric, hourly_data_gas, time_period="day", custom_days=None
    ):
        # Get total consumption for the time period
        total_electric_daily = sum(hourly_data_electric)
        total_gas_daily = sum(hourly_data_gas)

        # Scale based on selected time period
        scaling_factors = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
            "custom": custom_days if custom_days is not None else 1,
        }

        scaling = scaling_factors.get(time_period, 1)

        total_electric = total_electric_daily * scaling
        total_gas = total_gas_daily * scaling
        gas_to_kwh = total_gas * 10.55

        # UK grid average emissions factors:
        # ~0.23 kg CO2 per kWh of electricity
        # ~0.18 kg CO2 per kWh of gas
        return round(total_electric * 0.23 + gas_to_kwh * 0.18)

    # Calculate energy intensity (kWh/m²/yr)
    def calculate_energy_intensity(
        self, total_consumption, building_area, time_period="day", custom_days=None
    ):
        if not building_area:
            return 0

        # Energy intensity should always be per year for comparison purposes
        # If total_consumption is not already annual, scale it
        if time_period != "year":
            # Scale consumption to annual based on time period
            scaling_factors = {
                "day": 365,
                "week": 52,
                "month": 12,
                "year": 1,
                "custom": 365 / custom_days if custom_days else 365,
            }
            scaling = scaling_factors.get(time_period, 365)
            annual_consumption = total_consumption * scaling
        else:
            annual_consumption = total_consumption

        return round(annual_consumption / building_area)

    # Estimate renewable energy percentage based on building energy class
    def estimate_renewable_percentage(self, energy_class):
        renewable_mapping = {"A+": 45, "A": 35, "B": 25, "C": 15, "D": 10, "E": 5}
        return renewable_mapping.get(energy_class, 15)

    # Calculate water intensity (L/m²/yr)
    def calculate_water_intensity(
        self, hourly_data_water, building_area, time_period="day", custom_days=None
    ):
        if not building_area:
            return 0

        # Daily water consumption - sum of hourly values
        total_water_daily = sum(hourly_data_water)

        # Scale to annual based on time period
        scaling_factors = {
            "day": 365,
            "week": 52,
            "month": 12,
            "year": 1,
            "custom": 365 / custom_days if custom_days else 365,
        }

        scaling = scaling_factors.get(time_period, 365)
        annual_water = total_water_daily * scaling

        # Return water intensity in L/m²/yr
        return round(annual_water / building_area)


class CommunityEngagement:
    ### FR5 Logic ###
    def __init__(self, user: Optional[User] = None):
        self.user = user

    def add_display_names_to_activities(self, activities, activity_types_dict):
        # Handle both single activity and list of activities
        if not isinstance(activities, list):
            activities = [activities]

        for activity in activities:
            # Convert internal db code to display name if it exists in the dictionary
            if activity.activity_type in activity_types_dict:
                activity.display_name = activity_types_dict[activity.activity_type][
                    "name"
                ]
            else:
                # Keep original value if not found in dictionary
                # Example: "cycling" -> "Cycled to Campus", but "unknown_activity" stays as "unknown_activity"
                activity.display_name = activity.activity_type

        return activities

    def log_activity(self, activity: SustainableActivity):
        if not self.user or not activity:
            return {"error": "Invalid user or activity"}, 400

        user_activity = SustainableActivity(
            user_id=self.user.id,
            activity_type=activity.activity_type,
            description=activity.description,
            points_awarded=activity.points_awarded,
            carbon_saved=activity.carbon_saved,
            status="verified",
        )
        db.session.add(user_activity)
        self._update_user_points(activity)
        db.session.commit()

        total_points = 0
        if self.user and hasattr(self.user, "points") and self.user.points:
            total_points = self.user.points.total_points

        return {
            "message": f"Activity logged. {activity.points_awarded} points awarded.",
            "total_points": total_points,
        }, 200

    def submit_activity(
        self, activity_type: str, description: str = "", evidence: Optional[str] = None
    ):
        if not self.user:
            return {"error": "User not authenticated"}, 401

        try:
            activity = SustainableActivity(
                user_id=self.user.id,
                activity_type=activity_type,
                description=description,
                evidence=evidence or "",
                status="pending",
            )
            db.session.add(activity)
            db.session.commit()
            return {"message": "Activity submitted for review."}, 201
        except Exception as e:
            return {"error": str(e)}, 400

    def _update_user_points(self, activity: SustainableActivity):
        if not self.user:
            return

        if hasattr(self.user, "points") and self.user.points:
            self.user.points.total_points += activity.points_awarded
            self.user.points.green_score += activity.carbon_saved
        else:
            self.user.points = UserPoints(
                total_points=activity.points_awarded,
                green_score=activity.carbon_saved,
                user_id=self.user.id,
            )
            db.session.add(self.user.points)

    # FR6 logic
    def award_points(self, activity: SustainableActivity):
        if not self.user:
            return {"error": "Invalid user"}, 400

        if activity.points_awarded is not None:
            return {"error": "Points have already been awarded for this activity."}, 400

        # Award 10 points per kg CO2 saved (ensure int conversion)
        points_awarded = int(activity.carbon_saved * 10)
        activity.points_awarded = points_awarded

        total_points = 0
        if hasattr(self.user, "points") and self.user.points:
            self.user.points.total_points += points_awarded
            self.user.points.green_score += activity.carbon_saved
            total_points = self.user.points.total_points
        else:
            new_points = UserPoints(
                total_points=points_awarded,
                green_score=activity.carbon_saved,
                user_id=self.user.id,
            )
            self.user.points = new_points
            db.session.add(new_points)
            db.session.commit()
            total_points = points_awarded

        return {
            "message": f"Awarded {points_awarded} points for {activity.activity_type}",
            "total_points": total_points,
        }, 200

    # New methods for admin/user operations

    def get_user_points(self, user_id=None):
        """Get point information for a user"""
        if not self.user and not user_id:
            return 0

        user_id = user_id or (self.user.id if self.user else None)
        if not user_id:
            return 0

        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        return user_points.green_score if user_points else 0

    def get_top_users(self, limit=10):
        """Get top users by green score"""
        return (
            db.session.query(UserPoints, User)
            .join(User, UserPoints.user_id == User.id)
            .order_by(UserPoints.green_score.desc())
            .limit(limit)
            .all()
        )

    def get_recent_activities(self, user_id=None, limit=3):
        """Get recent activities for a user"""
        if not self.user and user_id is None:
            return []

        user_id = user_id or (self.user.id if self.user else None)
        if user_id is None:
            return []

        return (
            SustainableActivity.query.filter(SustainableActivity.user_id == user_id)
            .order_by(SustainableActivity.timestamp.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_pending_submissions():
        """Get all pending activity submissions"""
        return SustainableActivity.query.filter_by(status="pending").all()

    @staticmethod
    def update_activity_status(activity_id, status):
        """Update status of a sustainable activity"""
        if status not in ["verified", "rejected"]:
            return {"error": "Invalid status value"}, 400

        activity = SustainableActivity.query.get(activity_id)
        if not activity:
            return {"error": "Activity not found"}, 404

        activity.status = status
        db.session.commit()
        return {"message": f"Activity status updated to {status}"}, 200

    @staticmethod
    def update_user_role(user_id, new_role, current_user_id=None):
        """Update a user's role with validation"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        # Prevent self-demotion from Admin
        if current_user_id == user.id and new_role != "Admin" and user.role == "Admin":
            return {"error": "You cannot demote yourself from the Admin role"}, 400

        # Ensure at least one admin exists
        if user.role == "Admin" and new_role != "Admin":
            admins = User.query.filter_by(role="Admin").count()
            if admins <= 1:
                return {
                    "error": "There must be at least one user with the Admin role"
                }, 400

        user.role = new_role
        db.session.commit()
        return {"message": f"User role updated to {new_role}"}, 200
