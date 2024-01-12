@questionnaires_manager @pipeline_tests
Feature: questionnaires_manager
  As a user,
  I want to perform a CRUD action on the questionnaires_manager resource

@tag4
  Scenario: Basic get request for questionnaires_manager
    Given I setup the data by inserting from file questionnaires_manager_body into the dynamoDB table questionnaires
    When I request data for id=1025655242481666 from questionnaires
    Then I receive a status code 200 in response
    And I receive data for id 1025655242481666 in the response

@tag5
  Scenario: Basic post request for questionnaires_manager
    Given I reset the data by deleting id 1025655242481666 in the dynamoDB table questionnaires
    When I post the json questionnaires_manager_body to the resource questionnaires
    Then I receive a status code 200 in response
    And I can retrieve data for id 1025655242481666 in the dynamoDB table

@tag6
  Scenario: Basic delete request for questionnaires_manager
    Given I setup the data by inserting from file questionnaires_manager_body into the dynamoDB table questionnaires
    When I delete data for id 1025655242481666 from the resource questionnaires
    Then data for id 1025655242481666 in the dynamoDB table has been deleted
