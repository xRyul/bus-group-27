Feature: GreenScore Points Awarding
    As a sustainability administrator
    I want to award points for verified sustainable activities
    So that users are rewarded for their sustainable actions

    Scenario: Award points for a verified activity
        Given a sustainable activity exists in the system
        And the activity has not been awarded points yet
        When an administrator awards points for the activity
        Then points should be awarded based on carbon saved
        And the user's total points should be updated 