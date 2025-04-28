# =============================================================================
# BUILDING ENERGY (POSITIVE TEST CASE)
# =============================================================================
# - Verify the building energy data retrieval functionality
# 
# 1. Setup test environment with in-memory database
# 2. Verify a building exists in the system
# 3. Verify energy data exists for the building
# 4. Request energy data for the building
# 5. Verify the system returns valid energy data
# =============================================================================

import pytest
from pytest_bdd import given, when, then, scenario
from app.logic import BuildingEnergyMonitoring
from app.models.building import Building
from app import db, app
from app.debug_utils import reset_db

# =============================================================================
# 1. TEST SETUP AND CONFIGURATION
# =============================================================================
@pytest.fixture
def test_client():
    """
    Configure test environment with in-memory database.
    
    Sets up Flask test environment, initializes database with test data,
    and maintains app context throughout test execution.
    """
    # Configure app for isolated testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    # Create test client with context and initialize database
    with app.test_client() as client:
        with app.app_context():
            reset_db()
            yield client

# =============================================================================
# 2. TEST SCENARIO DEFINITION
# =============================================================================
@scenario('building_energy.feature', 'Get building energy data')
def test_get_building_energy_data():
    """
    Positive test for building energy data retrieval
    Verifies BuildingEnergyMonitoring can successfully retrieve
    energy consumption data using BDD methodology
    """
    pass  # pytest-bdd implements the test from the building_energy.feature file

# =============================================================================
# 3. TEST STEPS IMPLEMENTATION
# =============================================================================
# 3.1. GIVEN: Building exists in system
@given('a building exists in the system', target_fixture='building')
def get_building(test_client):
    """
    Verify a building exists and return it for testing
    Requires test_client to ensure database initialization
    """
    building = db.session.query(Building).first()
    assert building is not None, "No building found in test database"
    return building

# 3.2. GIVEN: Energy data exists for building
@given('energy data exists for the building')
def energy_data_exists(building):
    # Verify the building has associated energy readings
    count = building.energy_readings.count()
    assert count > 0, f"Building {building.id} has no energy readings"

# 3.3. WHEN: Request energy data
@when('I request energy data for the building', target_fixture='energy_data_result')
def get_energy_data(building):
    """
    Request energy data and verify singleton pattern
    
    Creates two BuildingEnergyMonitoring instances to verify 
    singleton behavior before retrieving energy data
    """
    # Create two instances to verify singleton behavior
    monitoring1 = BuildingEnergyMonitoring()
    monitoring2 = BuildingEnergyMonitoring()
    
    # Verify singleton pattern works (both instances are the same object)
    assert monitoring1 is monitoring2, "BuildingEnergyMonitoring is not working as a singleton"
    
    # Request energy data using the singleton instance
    return monitoring1.get_hourly_average("electricity", building.id)

# 3.4. THEN: Verify energy data received
@then('I should receive the energy data')
def verify_energy_data(energy_data_result):
    """Verify energy data was successfully retrieved."""
    assert energy_data_result is not None, "Energy data result should not be None"
    assert len(energy_data_result) > 0, "Energy data should contain values"
