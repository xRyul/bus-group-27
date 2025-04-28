import json
from datetime import datetime
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import (
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app import app, db
from app.debug_utils import activity_types
from app.forms import LoginForm, UserSubmission
from app.logic import BuildingEnergyMonitoring, CommunityEngagement
from app.models.sustainable_activity import SustainableActivity
from app.models.user import User


@app.route("/")
def home():
    return render_template("landing_page.html", title="Home")


@app.route("/green_score", methods=["GET", "POST"])
@login_required
def green_score():
    now = datetime.now()
    last_updated = now.strftime("%H:%M:%S")

    # Use service layer - convert current_user to User type for type checking
    community_engagement = CommunityEngagement(User.query.get(current_user.id))

    # Get user points and top 10 users using service layer
    green_score = community_engagement.get_user_points()
    top_10 = community_engagement.get_top_users(10)

    form = UserSubmission()
    if form.validate_on_submit():
        # Use the service layer to submit the activity
        activity_type = form.activity_type.data
        description = form.description.data

        # Handle evidence - convert None to empty string to satisfy type requirements
        evidence = (
            form.evidence.data
            if hasattr(form, "evidence") and form.evidence.data
            else ""
        )

        result, status_code = community_engagement.submit_activity(
            activity_type=activity_type, description=description, evidence=evidence
        )

        if status_code == 201:
            flash(result["message"], "success")
        else:
            flash(result["error"], "danger")

        return redirect(url_for("green_score"))

    # Get recent activities using service layer
    recent_activities = community_engagement.get_recent_activities(limit=3)

    # Convert activity codes to display names
    community_engagement.add_display_names_to_activities(
        recent_activities, activity_types
    )

    return render_template(
        "green_score.html",
        title="Green Score",
        last_updated=last_updated,
        green_score=green_score,
        top_10=top_10,
        recent_activities=recent_activities,
        form=form,
    )


@app.route("/admin")
def admin():
    users = User.query.all()

    return render_template("admin.html", title="Admin", users=users)


@app.route("/user_submissions")
def user_submissions():
    # Use service layer to get pending submissions
    community_engagement = CommunityEngagement()
    submissions = community_engagement.get_pending_submissions()

    # Convert activity codes to display names
    community_engagement.add_display_names_to_activities(submissions, activity_types)

    return render_template(
        "user_submissions.html", title="User Submissions", submissions=submissions
    )


@app.route("/edit-role/<int:user_id>", methods=["POST"])
@login_required
def edit_role(user_id):
    new_role = request.form.get("role")

    # Use service layer to update user role
    community_engagement = CommunityEngagement()
    result, status_code = community_engagement.update_user_role(
        user_id, new_role, current_user.id
    )

    if status_code == 200:
        user = User.query.get(user_id)
        username = user.username if user else f"User {user_id}"
        flash(f"{username}'s role updated to {new_role}")
    else:
        flash(result["error"], "error")

    return redirect(url_for("admin"))


@app.route("/update_status/<int:submission_id>/<status>", methods=["POST"])
def update_status(submission_id, status):
    # Use service layer to update activity status
    community_engagement = CommunityEngagement()
    result, status_code = community_engagement.update_activity_status(
        submission_id, status
    )

    if status_code == 200:
        flash(f"The submission has been updated to {status}.", "success")
    else:
        flash(result["error"], "danger")

    return redirect(url_for("user_submissions"))


@app.route("/verify-activity/<int:activity_id>", methods=["POST"])
@login_required
def verify_activity(activity_id):
    if current_user.role not in ["Admin", "ST"]:
        flash("You don't have permission to verify activities", "danger")
        return redirect(url_for("admin"))

    activity = SustainableActivity.query.get_or_404(activity_id)

    if activity.activity_type in activity_types:
        # Use the predefined value from activity_types
        carbon_saved = activity_types[activity.activity_type]["carbon_saved"]
        points_awarded = activity_types[activity.activity_type]["points"]
    else:
        # Fallback to manual calculation if activity type not found
        carbon_saved = float(request.form.get("carbon_saved", 0))
        points_awarded = int(carbon_saved * 10)
    
    activity.status = "verified"
    activity.carbon_saved = carbon_saved
    activity.points_awarded = points_awarded
    db.session.commit()

    # Use service to award points to user's total (this updates UserPoints record, not the activity)
    user = User.query.get(activity.user_id)
    if user:
        community_engagement = CommunityEngagement(user)
        community_engagement.add_display_names_to_activities(activity, activity_types)

        result, status_code = community_engagement.award_points(activity)

        if status_code == 200:
            flash(result["message"], "success")
        else:
            flash(result["error"], "danger")
        db.session.commit()
    else:
        flash("User not found", "danger")

    return redirect(url_for("admin"))


@app.route("/building-energy-monitoring")
@login_required
def building_energy_monitoring():
    bem = BuildingEnergyMonitoring()

    # Get buildings and handle selection
    buildings = bem.get_all_buildings()
    if not buildings:
        flash("No buildings found in the database.", "error")
        return render_template(
            "building_energy_monitoring.html",
            title="Building Energy Monitoring",
            buildings=[],
            selected_building_id=None,
            selected_building=None,
            hourly_data_electric=[],
            hourly_data_gas=[],
            hourly_data_water=[],
            anomalies=[],
            anomaly_count=0,
            total_consumption=0,
            estimated_cost=0,
            carbon_footprint=0,
            energy_intensity=0,
            renewable_percent=0,
            water_intensity=0,
            time_period="day",
            custom_start_date=None,
            custom_end_date=None,
        )

    # Validate building selection
    selected_building_id = bem.validate_building_selection(
        request.args.get("building_id", type=int), buildings
    )

    # Get the selected building object
    selected_building = next(
        (b for b in buildings if b.id == selected_building_id), None
    )

    # Get energy data
    hourly_data_electric = bem.get_hourly_average("electric", selected_building_id)
    hourly_data_gas = bem.get_hourly_average("gas", selected_building_id)
    hourly_data_water = bem.get_hourly_average("water", selected_building_id)

    # Get anomalies
    anomalies_by_type = bem.get_anomalies_for_building(selected_building_id)
    anomaly_count = bem.get_anomaly_count(anomalies_by_type)

    # Get the selected time period from the frontend
    time_period = request.args.get("time_period", "day")
    custom_days = None
    custom_start_date = request.args.get("start_date")
    custom_end_date = request.args.get("end_date")

    # Handle custom date range
    if time_period == "custom" and custom_start_date and custom_end_date:
        try:

            start_date = datetime.strptime(custom_start_date, "%Y-%m-%d")
            end_date = datetime.strptime(custom_end_date, "%Y-%m-%d")
            # Calculate number of days in custom range
            custom_days = (
                end_date - start_date
            ).days + 1  # +1 to include both start and end dates

            if custom_days <= 0:
                custom_days = 1
                flash("Invalid date range. Using default values.", "warning")
        except ValueError:
            # If dates are invalid, default to 1 day
            custom_days = 1
            flash("Invalid date format. Using default values.", "warning")

    # Validate time period
    if time_period not in ["day", "week", "month", "year", "custom"]:
        time_period = "day"  # Default to day if invalid value

    # Calculate additional metrics for summary cards using service methods
    building_area = (
        selected_building.total_area
        if selected_building and selected_building.total_area
        else 3000
    )
    energy_class = selected_building.energy_class if selected_building else "C"

    # Calculate metrics using service methods with time period
    total_consumption = bem.calculate_total_consumption(
        hourly_data_electric, hourly_data_gas, time_period, custom_days
    )
    estimated_cost = bem.calculate_estimated_cost(
        hourly_data_electric, hourly_data_gas, time_period, custom_days
    )
    carbon_footprint = bem.calculate_carbon_footprint(
        hourly_data_electric, hourly_data_gas, time_period, custom_days
    )
    energy_intensity = bem.calculate_energy_intensity(
        total_consumption, building_area, time_period, custom_days
    )
    renewable_percent = bem.estimate_renewable_percentage(energy_class)
    water_intensity = bem.calculate_water_intensity(
        hourly_data_water, building_area, time_period, custom_days
    )

    return render_template(
        "building_energy_monitoring.html",
        title="Building Energy Monitoring",
        buildings=buildings,
        selected_building_id=selected_building_id,
        selected_building=selected_building,
        hourly_data_electric=hourly_data_electric,
        hourly_data_gas=hourly_data_gas,
        hourly_data_water=hourly_data_water,
        anomalies=anomalies_by_type,
        anomaly_count=anomaly_count,
        total_consumption=total_consumption,
        estimated_cost=estimated_cost,
        carbon_footprint=carbon_footprint,
        energy_intensity=energy_intensity,
        renewable_percent=renewable_percent,
        water_intensity=water_intensity,
        time_period=time_period,
        custom_start_date=custom_start_date,
        custom_end_date=custom_end_date,
    )


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("generic_form.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/export-building-data", methods=["POST"])
@login_required
def export_building_data():
    # Get export parameters from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    building_id = data.get("building_id")
    if not building_id:
        return jsonify({"error": "No building ID provided"}), 400

    # Extract export options
    export_options = {
        "include_electric": data.get("include_electric", False),
        "include_gas": data.get("include_gas", False),
        "include_water": data.get("include_water", False),
        "include_anomalies": data.get("include_anomalies", False),
        "include_summary": data.get("include_summary", False),
    }

    # Extract time period and custom dates if applicable
    time_period = data.get("time_period", "day")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    # Use BuildingEnergyMonitoring service to get the data
    bem = BuildingEnergyMonitoring()
    export_data = bem.export_building_data(
        building_id, export_options, time_period, start_date, end_date
    )

    if "error" in export_data:
        return jsonify({"error": export_data["error"]}), 400

    # Format the output based on requested format
    export_format = data.get("export_format", "json")

    if export_format == "json":
        # For JSON, we can just return the data
        return jsonify(export_data)
    elif export_format == "csv":
        # For CSV, we need to flatten the data
        csv_data = "timestamp,type,consumption_value,is_anomaly\n"

        # Add electric data if included
        if "electric_data" in export_data:
            for entry in export_data["electric_data"]:
                csv_data += f"{entry['timestamp']},electric,{entry['consumption_value']},{entry['is_anomaly']}\n"

        # Add gas data if included
        if "gas_data" in export_data:
            for entry in export_data["gas_data"]:
                csv_data += f"{entry['timestamp']},gas,{entry['consumption_value']},{entry['is_anomaly']}\n"

        # Add water data if included
        if "water_data" in export_data:
            for entry in export_data["water_data"]:
                csv_data += f"{entry['timestamp']},water,{entry['consumption_value']},{entry['is_anomaly']}\n"

        # Return CSV as a file download
        building_name = export_data["building"]["name"].replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{building_name}_energy_data_{timestamp}.csv"

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"},
        )
    else:
        return jsonify({"error": f"Unsupported export format: {export_format}"}), 400


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes


# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template("errors/403.html", title="Error"), 403


# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html", title="Error"), 404


@app.errorhandler(413)
def error_413(error):
    return render_template("errors/413.html", title="Error"), 413


# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template("errors/500.html", title="Error"), 500
