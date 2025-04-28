# =============================================================================
# POINTS AWARDING TESTS
# =============================================================================
"""
Tests for the Point/GreenScore Awarding functionality (FR6).

This file contains a positive test case:
1. POSITIVE TEST: Verifies successful awarding of points for verified sustainable activities

The test uses Behavior-Driven Development (BDD) methodology with Given-When-Then
steps defined in points_awarding.feature
"""

import pytest
from pytest_bdd import given, when, then, scenario
from app.logic import CommunityEngagement
from app.models.user import User
from app.models.sustainable_activity import SustainableActivity
from app.models.user_points import UserPoints
from app import db, app
from app.debug_utils import reset_db, activity_types

# =============================================================================
# TEST SETUP AND CONFIGURATION
# =============================================================================
@pytest.fixture
def test_client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            reset_db()
            yield client

# =============================================================================
# 1. POSITIVE TEST: POINTS AWARDING FOR VERIFIED ACTIVITY
# =============================================================================
@scenario('points_awarding.feature', 'Award points for a verified activity')
def test_award_points():
    pass

# 1.1 GIVEN: Sustainable activity exists
@given('a sustainable activity exists in the system', target_fixture='test_activity')
def create_test_activity(test_client):
    # Get first user from database
    user = db.session.query(User).first()
    assert user is not None, "No user found in test database"
    
    # Create a new activity for testing
    # - Activity is verified but no points awarded yet
    # - Carbon saved is set to a value for predictable point calculation
    # - points_awarded is set to 0, which now means "no points awarded yet"
    activity_type = next(iter(activity_types.keys()))
    activity = SustainableActivity(
        user_id=user.id,
        activity_type=activity_type,
        description="Test activity for points awarding",
        status="verified",  
        carbon_saved=5.0, 
        points_awarded=0    
    )
    
    db.session.add(activity)
    db.session.commit()
    
    # Get the created activity
    activity = db.session.query(SustainableActivity).filter_by(
        user_id=user.id,
        description="Test activity for points awarding"
    ).first()
    
    assert activity is not None, "Failed to create test activity"
    return activity

# 1.2 GIVEN: Activity has not been awarded points
@given('the activity has not been awarded points yet')
def verify_no_points_awarded(test_activity):
    assert test_activity.points_awarded == 0, \
        f"Activity already has points: {test_activity.points_awarded}"

# 1.3 WHEN: Administrator awards points
@when('an administrator awards points for the activity', target_fixture='award_result')
def award_points(test_activity):
    # Get the user who performed the activity
    user = db.session.query(User).get(test_activity.user_id)
    assert user is not None, "User not found"
    
    # Save initial points for verification
    initial_points = 0
    if hasattr(user, "points") and user.points:
        initial_points = user.points.total_points
    
    # Create CommunityEngagement service for the user
    community = CommunityEngagement(user)
    
    # Award points for the activity
    result, status_code = community.award_points(test_activity)
    
    return {
        'result': result,
        'status_code': status_code,
        'user_id': user.id,
        'activity_id': test_activity.id,
        'initial_points': initial_points
    }

# 1.4 THEN: Points should be awarded based on carbon saved
@then('points should be awarded based on carbon saved')
def verify_points_awarded(test_activity, award_result):
    # Refresh the activity from the database
    # Verify the points awarded is 10 points per kg CO2 saved - as per CommunityEngagement.award_points logic
    activity = db.session.query(SustainableActivity).get(award_result['activity_id'])
    assert activity.points_awarded > 0, "No points were awarded to the activity"
    expected_points = int(activity.carbon_saved * 10)
    assert activity.points_awarded == expected_points, f"Expected {expected_points} points, but got {activity.points_awarded}"

# 1.5 AND: User's total points should be updated
@then('the user\'s total points should be updated')
def verify_user_points_updated(award_result):
    # Get the user's current points
    user = db.session.query(User).get(award_result['user_id'])
    assert user is not None, "User not found"
    assert hasattr(user, "points") and user.points is not None, "User has no points record"
    
    # Get the activity to determine how many points were awarded
    activity = db.session.query(SustainableActivity).get(award_result['activity_id'])
    
    # Verify the user's total points were updated correctly
    expected_total = award_result['initial_points'] + activity.points_awarded
    assert user.points.total_points == expected_total, f"Expected user to have {expected_total} points, but got {user.points.total_points}"
