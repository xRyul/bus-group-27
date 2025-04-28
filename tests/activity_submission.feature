Feature: Sustainable Activity Submission
    As a user
    I want to submit sustainable activities
    So that I can contribute to campus sustainability efforts

    Scenario: Submit a sustainable activity
        Given a user is authenticated
        When I submit a sustainable activity
        Then the activity should be saved with "pending" status
        And I should receive a confirmation message
        
    Scenario: Submit activity without authentication
        Given no user is authenticated
        When I attempt to submit a sustainable activity
        Then an authentication error should be returned 