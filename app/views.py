import csv
import io
from datetime import datetime, time
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_login import (
    current_user,
    fresh_login_required,
    login_required,
    login_user,
    logout_user,
)

from app import app, db
from app.debug_utils import activity_types
from app.forms import ChooseForm, LoginForm, UserSubmission
from app.logic import BuildingEnergyMonitoring, CommunityEngagement
from app.models.building import Building
from app.models.building_energy import BuildingEnergy
from app.models.sustainable_activity import SustainableActivity
from app.models.user import User
from app.models.user_points import UserPoints


@app.route("/")
def home():
    return render_template("home.html", title="Home")


@app.route("/green_score", methods=["GET", "POST"])
@login_required
def green_score():
    now = datetime.now()
    last_updated = now.strftime("%H:%M:%S")

    # Use service layer
    community_engagement = CommunityEngagement(current_user)

    # Get actual user points from database
    user_points = UserPoints.query.filter_by(user_id=current_user.id).first()
    green_score = user_points.green_score if user_points else 0
    top_10 = (
        db.session.query(UserPoints, User)
        .join(User, UserPoints.user_id == User.id)
        .order_by(UserPoints.green_score.desc())
        .limit(10)
        .all()
    )

    form = UserSubmission()
    if form.validate_on_submit():
        # Use the service layer to submit the activity
        activity_type = form.activity_type.data
        description = form.description.data
        evidence = form.evidence.data if hasattr(form, "evidence") else None

        result, status_code = community_engagement.submit_activity(
            activity_type=activity_type, description=description, evidence=evidence
        )

        if status_code == 201:
            flash(result["message"], "success")
        else:
            flash(result["error"], "danger")

        return redirect(url_for("green_score"))

    recent_activities = (
        SustainableActivity.query.filter(SustainableActivity.user_id == current_user.id)
        .order_by(SustainableActivity.timestamp.desc())
        .limit(3)
        .all()
    )

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
    submissions = SustainableActivity.query.filter_by(status="pending").all()

    # Convert activity codes to display names
    # Create a community engagement service instance (user can be None for this operation)
    community_engagement = CommunityEngagement(None)
    community_engagement.add_display_names_to_activities(submissions, activity_types)

    return render_template(
        "user_submissions.html", title="User Submissions", submissions=submissions
    )


@app.route("/edit-role/<int:user_id>", methods=["POST"])
@login_required
def edit_role(user_id):
    user = User.query.get(user_id)
    new_role = request.form.get("role")

    if current_user.id == user.id and new_role != "Admin":
        flash("You cannot demote yourself from the Admin role.", "error")
        return redirect(url_for("admin"))

    if user.role == "Admin" and new_role != "Admin":
        admins = User.query.filter_by(role="Admin").count()
        if admins <= 1:
            flash("There must be at least one user with the Admin role.", "error")
            return redirect(url_for("admin"))

    user.role = new_role
    db.session.commit()
    flash(f"{user.username}'s role updated to {new_role}")

    return redirect(url_for("admin"))


@app.route("/update_status/<int:submission_id>/<status>", methods=["POST"])
def update_status(submission_id, status):
    submission = SustainableActivity.query.get(submission_id)
    if submission:
        if status in ["verified", "rejected"]:
            submission.status = status
            db.session.commit()

            flash(f"The submission has been updated to {status}.", "success")
        else:
            flash("Submission not found.", "danger")
    return redirect(url_for("user_submissions"))


@app.route("/verify-activity/<int:activity_id>", methods=["POST"])
@login_required
def verify_activity(activity_id):
    if current_user.role not in ["Admin", "ST"]:
        flash("You don't have permission to verify activities", "danger")
        return redirect(url_for("admin"))

    activity = SustainableActivity.query.get_or_404(activity_id)
    carbon_saved = float(request.form.get("carbon_saved", 0))

    activity.status = "verified"
    activity.carbon_saved = carbon_saved

    # Use service to award points
    user = User.query.get(activity.user_id)
    community_engagement = CommunityEngagement(user)

    # Add display name to activity (for logging/flash messages if needed)
    community_engagement.add_display_names_to_activities(activity, activity_types)

    result, status_code = community_engagement.award_points(activity)

    if status_code == 200:
        flash(result["message"], "success")
    else:
        flash(result["error"], "danger")

    db.session.commit()
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
            hourly_data_electric=[],
            hourly_data_gas=[],
            hourly_data_water=[],
            anomalies=[],
            anomaly_count=0,
        )

    # Validate building selection
    selected_building_id = bem.validate_building_selection(
        request.args.get("building_id", type=int), buildings
    )

    # Get energy data
    hourly_data_electric = bem.get_hourly_average("electric", selected_building_id)
    hourly_data_gas = bem.get_hourly_average("gas", selected_building_id)
    hourly_data_water = bem.get_hourly_average("water", selected_building_id)

    # Get anomalies
    anomalies_by_type = bem.get_anomalies_for_building(selected_building_id)
    anomaly_count = bem.get_anomaly_count(anomalies_by_type)

    return render_template(
        "building_energy_monitoring.html",
        title="Building Energy Monitoring",
        buildings=buildings,
        selected_building_id=selected_building_id,
        hourly_data_electric=hourly_data_electric,
        hourly_data_gas=hourly_data_gas,
        hourly_data_water=hourly_data_water,
        anomalies=anomalies_by_type,
        anomaly_count=anomaly_count,
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
