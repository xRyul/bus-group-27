# =============================================================================
# BUILDING ENERGY TESTS
# =============================================================================
"""
Tests for the Building Energy Monitoring (FR2)

1. POSITIVE TEST: Verifies successful retrieval of energy data for existing buildings
2. NEGATIVE TEST: Verifies proper handling when requesting data for non-existent buildings

Both tests use Behavior-Driven Development (BDD) methodology with Given-When-Then
steps defined in building_energy.feature
"""

import pytest
from pytest_bdd import given, when, then, scenario
from app.logic import BuildingEnergyMonitoring
from app.models.building import Building
from app import db, app
from app.debug_utils import reset_db

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
# 1. POSITIVE TEST: RETRIEVAL OF ENERGY DATA
# =============================================================================
@scenario('building_energy.feature', 'Get building energy data')
def test_get_building_energy_data():
    pass

# 1.1 GIVEN: Building exists in system
@given('a building exists in the system', target_fixture='building')
def get_building(test_client):
    building = db.session.query(Building).first()
    assert building is not None, "No building found in test database"
    return building

# 1.2 GIVEN: Energy data exists for building
@given('energy data exists for the building')
def energy_data_exists(building):
    count = building.energy_readings.count()
    assert count > 0, f"Building {building.id} has no energy readings"

# 1.3 WHEN: Request energy data
@when('I request energy data for the building', target_fixture='energy_data_result')
def get_energy_data(building):
    """
    Request energy data and verify singleton pattern
    
    Creates two BuildingEnergyMonitoring instances to verify 
    singleton behavior before retrieving energy data
    """

    monitoring1 = BuildingEnergyMonitoring()
    monitoring2 = BuildingEnergyMonitoring()
    
    # Verify singleton pattern works (both instances are the same object)
    assert monitoring1 is monitoring2, "BuildingEnergyMonitoring is not working as a singleton"
    
    # Request energy data using the singleton instance
    return monitoring1.get_hourly_average("electricity", building.id)

# 1.4 THEN: Verify energy data received
@then('I should receive the energy data')
def verify_energy_data(energy_data_result):
    assert energy_data_result is not None, "Energy data result should not be None"
    assert len(energy_data_result) > 0, "Energy data should contain values"


# =============================================================================
# 2. NEGATIVE TEST: HANDLING OF NON-EXISTENT BUILDINGS
# =============================================================================
@scenario('building_energy.feature', 'Get energy data for non-existent building')
def test_get_energy_data_for_invalid_building():
    pass

# 2.1 GIVEN: Non-existent building ID
@given('a non-existent building ID', target_fixture='invalid_id')
def non_existent_id(test_client):
    invalid_id = 9999
    building = db.session.query(Building).filter(Building.id == invalid_id).first()
    assert building is None, "Test error: Building with test ID should not exist"
    return invalid_id

# 2.2 WHEN: Request energy data for non-existent building
@when('I request energy data for the non-existent building', target_fixture='invalid_result')
def request_invalid_building_data(invalid_id):
    monitoring = BuildingEnergyMonitoring()
    return monitoring.get_hourly_average("electricity", invalid_id)

# 2.3 THEN: Verify default data returned
@then('I should receive default energy data')
def verify_default_data(invalid_result):
    assert invalid_result is not None, "Result should not be None even for invalid building"
    assert all(val == 0 for val in invalid_result), "Result should contain zeros for invalid building"
    assert len(invalid_result) == 24, "Result should have 24 hours of data (zeros)"
