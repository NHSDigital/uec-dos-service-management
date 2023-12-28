@healthcare_services
Feature: healthcare_services
  As a user,
  I want to perform a CRUD action on the healthcare_services resource

@tag4
  Scenario: Basic get request for healthcare_services
    Given I setup the data by inserting from file healthcareservices_body into the dynamoDB table healthcare_services
    When I request data for id=9 from healthcare_services
    Then I receive a status code 200 in response
    And I receive data for id 9 in the response

@tag1
  Scenario: Basic post request for healthcare_services
    Given I reset the data by deleting id 9 in the dynamoDB table healthcare_services
    When I post the json healthcareservices_body to the resource healthcare_services
    Then I receive a status code 200 in response
    And I can retrieve data for id 9 in the dynamoDB table

@tag6
  Scenario: Basic delete request for healthcare_services
    Given I setup the data by inserting from file healthcareservices_body into the dynamoDB table healthcare_services
    When I delete data for id 9 from the resource healthcare_services
    Then the data for id 9 in the dynamoDB table has been deleted

