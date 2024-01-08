@locations @pipeline_tests
Feature: location
  As a user,
  I want to perform a CRUD action on the locations resource

@tag4
  Scenario: Basic get request for locations
    Given I setup the data by inserting from file locations_body into the dynamoDB table locations
    When I request data for id=1025655242481332 from locations
    Then I receive a status code 200 in response
    And I receive data for id 1025655242481332 in the response

@tag5
  Scenario: Basic post request for locations
    Given I reset the data by deleting id 1025655242481332 in the dynamoDB table locations
    When I post the json locations_body to the resource locations
    Then I receive a status code 200 in response
    And I can retrieve data for id 1025655242481332 in the dynamoDB table

@tag6
  Scenario: Basic delete request for locations
    Given I setup the data by inserting from file locations_body into the dynamoDB table locations
    When I delete data for id 1025655242481332 from the resource locations
    Then data for id 1025655242481332 in the dynamoDB table has been deleted


