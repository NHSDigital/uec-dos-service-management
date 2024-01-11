@questionnaire_responses @pipeline_tests
Feature: questionnaire_responses
  As a user,
  I want to perform a CRUD action on the questionnaire_responses resource

@tag4
  Scenario: Basic get request for questionnaire_responses
    Given I setup the data by inserting from file questionnaire_responses_body into the dynamoDB table questionnaire_responses
    When I request data for id=1025655242481777 from questionnaire_responses
    Then I receive a status code 200 in response
    And I receive data for id 1025655242481777 in the response

@tag5
  Scenario: Basic post request for questionnaire_responses
    Given I reset the data by deleting id 1025655242481777 in the dynamoDB table questionnaire_responses
    When I post the json questionnaire_responses_body to the resource questionnaire_responses
    Then I receive a status code 200 in response
    And I can retrieve data for id 1025655242481777 in the dynamoDB table

@tag6
  Scenario: Basic delete request for questionnaire_responses
    Given I setup the data by inserting from file questionnaire_responses_body into the dynamoDB table questionnaire_responses
    When I delete data for id 1025655242481777 from the resource questionnaire_responses

