Feature: healthcare_services
  As a user,
  I want to perform a CRUD action on the healthcare_services resource

@tag4
  Scenario: Basic healthcare_services request
    Given I send a request to the resource healthcare_services
    # Then I receive a status code 200 in response
    #And I receive the message Item Deleted Successfully in response

@tag4
  Scenario: Basic healthcare_services request
    Given I request data for id=1 from healthcare_services
    Then I receive a status code 200 in response
    And I can get data for id 1 in the dynamoDB table
    # And I receive the message Item Deleted Successfully in response

@tag1
  Scenario: Basic healthcare_services request
    Given I can delete data for id 4 in the dynamoDB table healthcare_services
    And I post a request to the resource healthcare_services
    Then I receive a status code 200 in response
    And I can get data for id 4 in the dynamoDB table
    # And I receive the message Item Deleted Successfully in response
