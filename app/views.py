from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory, jsonify
from app import app
from app.models.user import User
from app.forms import ChooseForm, LoginForm, UserSubmission
from flask_login import current_user, login_user, logout_user, login_required, fresh_login_required
import sqlalchemy as sa
from app import db
from urllib.parse import urlsplit
import csv
import io
from datetime import datetime, time
from sqlalchemy import func, extract
from app.logic import BuildingEnergyMonitoring # Keep for potential future use or side effects, though not directly used for data retrieval now
from app.models.building import Building
from app.models.building_energy import BuildingEnergy


@app.route("/")
def home():
    return render_template('home.html', title="Home")

@app.route("/green_score", methods=['GET', 'POST'])
def green_score():
    now = datetime.now()
    last_updated = now.strftime("%H:%M:%S")
    green_score = 850
    form = UserSubmission()
    if form.validate_on_submit():
        return redirect(url_for('green_score'))
    return render_template('green_score.html', title="Green Score", last_updated=last_updated,
                            green_score=green_score, form=form)

@app.route("/admin")
def admin():
    users = User.query.all()

    submissions = [
        {'submission_date': '2025-04-01', 'username': 'amy', 'type': 'Recycling', 'proof': 'image'},
        {'submission_date': '2025-04-02', 'username': 'tom', 'type': 'Attending Event', 'proof': 'video'},
        {'submission_date': '2025-04-03', 'username': 'yin', 'type': 'Energy Saving', 'proof': 'image'},
        {'submission_date': '2025-04-04', 'username': 'tariq', 'type': 'Waste Reporting', 'proof': 'video'},
        {'submission_date': '2025-04-05', 'username': 'jo', 'type': 'Walking or Biking', 'proof': 'image'},

        {'submission_date': '2025-04-06', 'username': 'amy', 'type': 'Water Conservation', 'proof': 'video'},
        {'submission_date': '2025-04-07', 'username': 'tom', 'type': 'Recycling', 'proof': 'image'},
        {'submission_date': '2025-04-08', 'username': 'yin', 'type': 'Waste Reporting', 'proof': 'video'},
        {'submission_date': '2025-04-09', 'username': 'tariq', 'type': 'Energy Saving', 'proof': 'image'},
        {'submission_date': '2025-04-10', 'username': 'jo', 'type': 'Attending Event', 'proof': 'video'},

        {'submission_date': '2025-04-11', 'username': 'amy', 'type': 'Walking or Biking', 'proof': 'image'},
        {'submission_date': '2025-04-12', 'username': 'tom', 'type': 'Water Conservation', 'proof': 'video'},
        {'submission_date': '2025-04-13', 'username': 'yin', 'type': 'Recycling', 'proof': 'image'},
        {'submission_date': '2025-04-14', 'username': 'tariq', 'type': 'Attending Event', 'proof': 'video'},
        {'submission_date': '2025-04-15', 'username': 'jo', 'type': 'Waste Reporting', 'proof': 'image'}
    ]

    return render_template('admin.html', title="Admin", users=users,submissions=submissions)

@app.route("/edit-role/<int:user_id>", methods=["POST"])
@login_required
def edit_role(user_id):
    user = User.query.get(user_id)
    new_role = request.form.get("role")

    if user.role == 'Admin' and new_role != 'Admin':
        admins = User.query.filter_by(role='Admin').count()
        if admins <= 1:
            flash('There must be at least one user with the Admin role.', 'error')
            return redirect(url_for('admin'))

    user.role = new_role
    db.session.commit()
    flash(f"{user.username}'s role updated to {new_role}")

    return redirect(url_for("admin"))


@app.route("/building-energy-monitoring")
@login_required
def building_energy_monitoring():
    # Get the Building ID for "Computer Science"
    cs_building = db.session.scalar(sa.select(Building).where(Building.name == "Computer Science"))
    
    if not cs_building:
        flash("Computer Science building data not found.", "error")
        return render_template('building_energy_monitoring.html', title="Building Energy Monitoring", hourly_data=[], anomalies=[], anomaly_count=0)

    building_id = cs_building.id

    # Helper function to query average hourly data for a given energy type
    def get_hourly_average(energy_type):
        avg_data = db.session.query(
            extract('hour', BuildingEnergy.timestamp).label('hour'),
                func.avg(BuildingEnergy.consumption_value).label('average_consumption')
            ).filter(
                BuildingEnergy.building_id == building_id,
                BuildingEnergy.energy_type == energy_type,
                BuildingEnergy.is_anomaly.is_(True)
            ).group_by(extract('hour', BuildingEnergy.timestamp)
            ).order_by(extract('hour', BuildingEnergy.timestamp)
            ).all()
        # Prepare list (ensure all 24 hours are present, default to 0)
        data_dict = {hour: avg for hour, avg in avg_data}
        return [data_dict.get(h, 0) for h in range(24)]

    # Query average hourly consumption for electric, gas, and water
    hourly_data_electric = get_hourly_average('electric')
    hourly_data_gas = get_hourly_average('gas')
    hourly_data_water = get_hourly_average('water')

    # Query anomalies for electric only
    # If anomalies for gas/water are needed later, this query can be adjusted
    anomaly_records = db.session.query(
        BuildingEnergy.timestamp,
        BuildingEnergy.consumption_value
    ).filter(
        BuildingEnergy.building_id == building_id,
        BuildingEnergy.energy_type == 'electric', 
        BuildingEnergy.is_anomaly.is_(True)
    ).order_by(
        BuildingEnergy.timestamp
    ).all()

    # Prepare anomalies list in the format expected by the chart
    anomalies = []
    for timestamp, value in anomaly_records:
        # Calculate the index based on the timestamp e.g. hour
        hour_index = timestamp.hour
        anomalies.append({"index": hour_index, "value": value})

    anomaly_count = len(anomalies)

    return render_template(
        'building_energy_monitoring.html',
        title="Building Energy Monitoring",
        hourly_data_electric=hourly_data_electric,
        hourly_data_gas=hourly_data_gas,
        hourly_data_water=hourly_data_water,
        anomalies=anomalies,
        anomaly_count=anomaly_count
    )


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('generic_form.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500
