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
from datetime import datetime
from app.logic import BuildingEnergyMonitoring


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

@app.route("/building-energy-monitoring")
@login_required
def building_energy_monitoring():
    # Initialize the BuildingEnergyMonitoring class
    bem = BuildingEnergyMonitoring()
    
    # Get hourly data for the Computer Science building
    hourly_data = []
    for hour in range(24):
        # Get the average value for each hour (excluding anomalies)
        values = bem.hourly_data["Computer Science"]["electric"][hour]
        # Filter out anomalies for average calculation
        filtered_values = [v for v in values if v not in [12, 250, 220]]  # Known anomalies
        hourly_data.append(sum(filtered_values) / len(filtered_values))
    
    # Get anomalies
    anomalies = []
    outlier_dict = bem.detect_per_hour_iqr_anomalies()
    for day_index, day_outliers in outlier_dict.items():
        for hour, value in day_outliers.items():
            anomalies.append({"index": int(hour), "value": value})
    
    # Count total anomalies
    anomaly_count = len(anomalies)
    
    return render_template(
        'building_energy_monitoring.html', 
        title="Building Energy Monitoring",
        hourly_data=hourly_data,
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
