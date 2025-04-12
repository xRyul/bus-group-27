from app import db
from app.logic import BuildingEnergyMonitoring
from app.models.building import Building
from app.models.user import User

def reset_db():
    db.drop_all()
    db.create_all()

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
    #         description = f'Mock{activity_types[activity_type]['name']}'
    #         status = random.choice(['pending','verified','rejected'])

    #     days_ago = random.randint(0,30)
    #     timestamop = datetime.now() - timedelta(days=days_ago)
    #     activity = SustainableActivity(user_id=user_id, description=description,
    #                                    timestamp=timestamp, status=status)
    #     if status == 'verified':
    #         activity.points_awarded = activity_types[activity_type]['points']
    #         activity.carbon_saved = activity_types[activity_type]['carbon_saved']

    #         activities.append(activity)
            
    #     db.session.add_all(activities)
    #     db.session.commit()

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

    buildings = [
        {'name': 'Computer Science', 'location': 'Edgbaston Campus', 'total_area': 3200, 'energy_class': 'A'},
        {'name': 'Physics', 'location': 'Edgbaston Campus', 'total_area': 3000, 'energy_class': 'B'},
        {'name': 'Library', 'location': 'Edgbaston Campus', 'total_area': 4100, 'energy_class': 'A+'},
    ]

    for b in buildings:
        building = Building(**b)
        db.session.add(building)
    db.session.commit()

    BuildingEnergyMonitoring()

