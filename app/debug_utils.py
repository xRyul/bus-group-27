
from datetime import datetime, timedelta
import random
import numpy as np
from app import db
from app.models.building import Building
from app.models.building_energy import BuildingEnergy
from app.models.sustainable_activity import SustainableActivity
from app.models.user import User

from app.models.user_points import UserPoints
from app.logic import BuildingEnergyMonitoring

def reset_db():
    db.drop_all()
    db.create_all()
    
    create_users()
    create_buildings()
    generate_energy_data()



# ------------------- 1 ENERGY MONITORING ---------------------
def create_users():
    # User list with roles.
    # 'ST' = Sustainability Team
    # 'UL' = University Leadership
    users = [
        {'username': 'amy', 'email': 'amy@b.com', 'role': 'Admin', 'pw': 'p123'},
        {'username': 'tom', 'email': 'tom@b.com', 'role': 'Student', 'pw': 'p123'},
        {'username': 'yin', 'email': 'yin@b.com', 'role': 'Admin', 'pw': 'p123'},
        {'username': 'tariq', 'email': 'trq@b.com', 'role': 'Staff', 'pw': 'p123'},
        {'username': 'jo', 'email': 'jo@b.com', 'role': 'Facilities', 'pw': 'p123'},
        {'username': 'lee', 'email': 'lee@b.com', 'role': 'UL', 'pw': 'p123'},
        {'username': 'nina', 'email': 'nina@b.com', 'role': 'Student', 'pw': 'p123'},
        {'username': 'omar', 'email': 'omar@b.com', 'role': 'ST', 'pw': 'p123'},
        {'username': 'lisa', 'email': 'lisa@b.com', 'role': 'Staff', 'pw': 'p123'},
        {'username': 'zane', 'email': 'zane@b.com', 'role': 'Facilities', 'pw': 'p123'},
        {'username': 'ella', 'email': 'ella@b.com', 'role': 'Student', 'pw': 'p123'},
        {'username': 'kai', 'email': 'kai@b.com', 'role': 'UL', 'pw': 'p123'},
        {'username': 'maya', 'email': 'maya@b.com', 'role': 'Admin', 'pw': 'p123'},
        {'username': 'raj', 'email': 'raj@b.com', 'role': 'Student', 'pw': 'p123'},
        {'username': 'ken', 'email': 'ken@b.com', 'role': 'ST', 'pw': 'p123'},
        {'username': 'mia', 'email': 'mia@b.com', 'role': 'UL', 'pw': 'p123'},
        {'username': 'zoe', 'email': 'zoe@b.com', 'role': 'Staff', 'pw': 'p123'},
        {'username': 'ian', 'email': 'ian@b.com', 'role': 'Facilities', 'pw': 'p123'},
        {'username': 'beck', 'email': 'beck@b.com', 'role': 'Student', 'pw': 'p123'},
        {'username': 'ruth', 'email': 'ruth@b.com', 'role': 'Admin', 'pw': 'p123'}
    ]

    for u in users:
        # get the password value and remove it from the dict:
        pw = u.pop('pw')
        # create a new user object using the parameters defined by the remaining entries in the dict:
        user = User(**u)
        # set the password for the user object:
        user.set_password(pw)
        # add the newly created user object to the database session:
        db.session.add(user)
    db.session.commit()

def create_buildings():
    buildings = [
        {'name': 'Computer Science', 'location': 'Edgbaston Campus', 'total_area': 3200, 'energy_class': 'A'},
        {'name': 'Physics', 'location': 'Edgbaston Campus', 'total_area': 3000, 'energy_class': 'B'},
        {'name': 'Library', 'location': 'Edgbaston Campus', 'total_area': 4100, 'energy_class': 'A+'},
    ]

    for b in buildings:
        building = Building(**b)
        db.session.add(building)
    db.session.commit()

def generate_energy_data():
    """Generate simulated energy data for buildings"""
    raw_data = []
    processed_data = []
    anomaly_lookup = set()
    
    # Get building IDs from database
    building_map = {b.name: b.id for b in Building.query.all()}
    
    simulate_midweek_energy_readings(raw_data, building_map)
    inject_known_anomalies(raw_data)
    detect_anomalies_iqr(raw_data, anomaly_lookup)
    create_model_objects(raw_data, anomaly_lookup, processed_data)
    
    # Save to database
    db.session.add_all(processed_data)
    db.session.commit()

def simulate_midweek_energy_readings(raw_data, building_map):
    buildings = ["Computer Science", "Physics", "Library"]
    energy_types = {
        "electric": ("kWh", 80, 160),
        "water": ("litres", 150, 250),
        "gas": ("m3", 2.5, 4.5)
    }

    start_day = datetime(2025, 4, 11)
    intervals_per_day = 96

    for building in buildings:
        building_id = building_map[building]
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
                raw_data.append((building_id, timestamp, energy_type, value, unit))

def inject_known_anomalies(raw_data):
    updated = []
    for (building_id, timestamp, energy_type, value, unit) in raw_data:
        if (
            (timestamp.hour == 8 and timestamp.minute == 0 and energy_type == "electric") or
            (timestamp.hour == 14 and energy_type == "water")
        ):
            # Exaggerate electric/water anomalies by multiplying
            value = round(value * 2.5, 2) 
        elif (timestamp.hour == 20 and energy_type == "gas"):
             # Exaggerate gas
             value = round(value + 5.0, 2) 
        updated.append((building_id, timestamp, energy_type, value, unit))
    raw_data[:] = updated

def detect_anomalies_iqr(raw_data, anomaly_lookup, k=1.5):
    grouped = {}
    timestamps = {}
    
    for building_id, timestamp, energy_type, value, unit in raw_data:
        key = (building_id, energy_type)
        if key not in grouped:
            grouped[key] = []
            timestamps[key] = []
        grouped[key].append(value)
        timestamps[key].append(timestamp)

    for (building_id, energy_type), values in grouped.items():
        values_array = np.array(values)
        q1 = np.percentile(values_array, 25)
        q3 = np.percentile(values_array, 75)
        iqr = q3 - q1
        lower = q1 - k * iqr
        upper = q3 + k * iqr

        for i, val in enumerate(values):
            if val < lower or val > upper:
                ts = timestamps[(building_id, energy_type)][i]
                anomaly_lookup.add((building_id, energy_type, ts))

def create_model_objects(raw_data, anomaly_lookup, processed_data):
    for building_id, timestamp, energy_type, value, unit in raw_data:
        is_anomaly = (building_id, energy_type, timestamp) in anomaly_lookup
        model_instance = BuildingEnergy(
            building_id=building_id,
            timestamp=timestamp,
            energy_type=energy_type,
            consumption_value=value,
            unit=unit,
            is_anomaly=is_anomaly
        )
        processed_data.append(model_instance)


# ------------------- 2 SUSTAINABLE ACTIVITIES ---------------------

# activity_types = {
#     'cycling':{'name':'Cycled to Campus','points':10,'carbon_saved':2.5},
#     'public_transport': {'name': 'Used public transport', 'points': 5, 'carbon_saved': 1.2},
#     'recycling': {'name': 'Recycled materials', 'points': 3, 'carbon_saved': 0.8},
#     'reusable_container': {'name': 'Used Reusable Container', 'points': 2, 'carbon_saved': 0.3},
#     'event_participation': {'name': 'Attended Sustainability Event', 'points': 15, 'carbon_saved': 0.5},
#     'energy_saving': {'name': 'Reported Energy Waste', 'points': 8, 'carbon_saved': 5.0},
#     'water_saving': {'name': 'Reported Water Waste', 'points': 8, 'carbon_saved': 3.0},
#     'e-scooter': {'name': 'Used an e-scooter', 'points': 12, 'carbon_saved': 2.0},
# }

# def generate_mock_activities(self, user_ids, count=50):
#     activities = []
#     activity_type = list(activity_types.keys())

#     for _ in range(count):
#         user_id = random.choice(user_ids)
#         activity_type = random.choice(activity_types)
#         description = f"Mock{activity_types[activity_type]['name']}"
#         status = random.choice(['pending','verified','rejected'])

#     days_ago = random.randint(0,30)
#     timestamop = datetime.now() - timedelta(days=days_ago)
#     activity = SustainableActivity(user_id=user_id, description=description,
#                                 timestamp=timestamp, status=status)
#     if status == 'verified':
#         activity.points_awarded = activity_types[activity_type]['points']
#         activity.carbon_saved = activity_types[activity_type]['carbon_saved']

#         activities.append(activity)
        
#     db.session.add_all(activities)
#     db.session.commit()

