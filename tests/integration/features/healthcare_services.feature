Feature: healthcare_services
  As a user,
  I want to perform a CRUD action on the healthcare_services resource

@tag1
  Scenario: Basic healthcare_services request
    Given I send a request to the resource healthcare_services
    Then I receive a status code 200 in response
    And I receive the message Item Deleted Successfully in response

