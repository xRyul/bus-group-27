Feature: Building Energy Monitoring
    As a user
    I want to view building energy data
    So that I can monitor energy consumption

    Scenario: Get building energy data
        Given a building exists in the system
        And energy data exists for the building
        When I request energy data for the building
        Then I should receive the energy data 