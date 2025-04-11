from app import db
from app.logic import BuildingEnergyMonitoring
from app.models.building import Building
from app.models.user import User

def reset_db():
    db.drop_all()
    db.create_all()

    users =[
        {'username': 'amy',   'email': 'amy@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'username': 'tom',   'email': 'tom@b.com',                  'pw': 'amy.pw'},
        {'username': 'yin',   'email': 'yin@b.com', 'role': 'Admin', 'pw': 'amy.pw'},
        {'username': 'tariq', 'email': 'trq@b.com',                  'pw': 'amy.pw'},
        {'username': 'jo',    'email': 'jo@b.com',                   'pw': 'amy.pw'}
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

