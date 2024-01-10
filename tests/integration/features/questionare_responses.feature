@questionare_responses @pipeline_tests
Feature: questionare_responses
  As a user,
  I want to perform a CRUD action on the questionare_responses resource

@tag4
  Scenario: Basic get request for questionare_responses
    Given I setup the data by inserting from file questionare_responses_body into the dynamoDB table questionare_responses
    When I request data for id=1025655242481777 from questionare_responses
    Then I receive a status code 200 in response
    And I receive data for id 1025655242481777 in the response

@tag5
  Scenario: Basic post request for questionare_responses
    Given I reset the data by deleting id 1025655242481777 in the dynamoDB table questionare_responses
    When I post the json questionare_responses_body to the resource questionare_responses
    Then I receive a status code 200 in response
    And I can retrieve data for id 1025655242481777 in the dynamoDB table

@tag6
  Scenario: Basic delete request for questionare_responses
    Given I setup the data by inserting from file questionare_responses_body into the dynamoDB table questionare_responses
    When I delete data for id 1025655242481777from the resource questionare_responses
    Then data for id 1025655242481777 in the dynamoDB table has been deleted
