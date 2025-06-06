# =============================================================================
# SUSTAINABLE ACTIVITY SUBMISSION TESTS
# =============================================================================
"""
Tests for the Sustainable Activity Submission (FR5)

1. POSITIVE TEST: Verifies successful submission of sustainable activities by authenticated users
2. NEGATIVE TEST: Verifies proper handling when non-authenticated users attempt to submit activities

The tests use Behavior-Driven Development (BDD) methodology with Given-When-Then
steps defined in activity_submission.feature
"""

import pytest
from pytest_bdd import given, when, then, scenario
from app.logic import CommunityEngagement
from app.models.user import User
from app.models.sustainable_activity import SustainableActivity
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
# 1. POSITIVE TEST: SUCCESSFUL ACTIVITY SUBMISSION
# =============================================================================
@scenario('activity_submission.feature', 'Submit a sustainable activity')
def test_submit_activity():
    pass

# 1.1 GIVEN: User is authenticated
@given('a user is authenticated', target_fixture='authenticated_user')
def authenticated_user(test_client):
    # Get first user from database
    user = db.session.query(User).first()
    assert user is not None, "No user found in test database"
    return user

# 1.2 WHEN: Submit activity
@when('I submit a sustainable activity', target_fixture='submission_result')
def submit_activity(authenticated_user):
    # Create CommunityEngagement with the authenticated user
    community = CommunityEngagement(authenticated_user)
    
    # Get first activity type from predefined types
    activity_type = next(iter(activity_types.keys()))
    description = "Test activity description"
    
    # Submit the activity
    result, status_code = community.submit_activity(activity_type=activity_type, description=description)
    
    return {
        'result': result,
        'status_code': status_code,
        'user_id': authenticated_user.id,
        'activity_type': activity_type
    }

# 1.3 THEN: Verify activity saved with pending status
@then('the activity should be saved with "pending" status')
def verify_activity_saved(submission_result):
    # Query the database to verify the activity was saved
    activity = db.session.query(SustainableActivity).filter_by(
        user_id=submission_result['user_id'],
        activity_type=submission_result['activity_type']
    ).order_by(SustainableActivity.id.desc()).first()
    
    assert activity is not None, "Activity was not saved to the database"
    assert activity.status == "pending", f"Activity status should be 'pending', got '{activity.status}'"

# 1.4 AND: Verify confirmation message
@then('I should receive a confirmation message')
def verify_confirmation_message(submission_result):
    # Verify the status code is 201 (Created)
    assert submission_result['status_code'] == 201, f"Expected status code 201, got {submission_result['status_code']}"
    
    # Verify the result contains a success message
    assert 'message' in submission_result['result'], "Result should contain a 'message' key"
    assert "submitted for review" in submission_result['result']['message'], "Message should indicate activity was submitted for review"

# =============================================================================
# 2. NEGATIVE TEST: HANDLING OF NON-AUTHENTICATED USERS
# =============================================================================
@scenario('activity_submission.feature', 'Submit activity without authentication')
def test_submit_activity_without_auth():
    pass

# 2.1 GIVEN: No user is authenticated
@given('no user is authenticated', target_fixture='unauthenticated')
def no_authenticated_user():
    # Create a CommunityEngagement instance with no user
    return CommunityEngagement(user=None)

# 2.2 WHEN: Attempt to submit activity
@when('I attempt to submit a sustainable activity', target_fixture='error_result')
def attempt_submit_without_auth(unauthenticated):
    # Attempt to submit an activity without authentication
    activity_type = next(iter(activity_types.keys()))
    description = "This should fail"
    
    # Submit the activity expecting to fail
    result, status_code = unauthenticated.submit_activity(
        activity_type=activity_type,
        description=description
    )
    
    return {
        'result': result,
        'status_code': status_code
    }

# 2.3 THEN: Verify authentication error
@then('an authentication error should be returned')
def verify_auth_error(error_result):
    # Verify the status code is 401 (Unauthorized)
    assert error_result['status_code'] == 401, f"Expected status code 401, got {error_result['status_code']}"
    
    # Verify the result contains an error message
    assert 'error' in error_result['result'], "Result should contain an 'error' key"
    assert "not authenticated" in error_result['result']['error'].lower(), "Error should indicate user is not authenticated"
