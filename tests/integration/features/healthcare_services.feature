Feature: healthcare_services
  As a user,
  I want to perform a CRUD action on the healthcare_services resource

@tag4
  Scenario: Basic healthcare_services get request
    Given I request data for id=1 from healthcare_services
    Then I receive a status code 200 in response
    And I can retrieve data for id 1 in the dynamoDB table

@tag1
  Scenario: Basic healthcare_services post request
    Given I reset the data by deleting id 9 in the dynamoDB table healthcare_services
    When I post the json healthcareservices_body to the resource healthcare_services
    Then I receive a status code 200 in response
    And I can retrieve data for id 9 in the dynamoDB table

