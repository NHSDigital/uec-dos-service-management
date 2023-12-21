Feature: location
  As a user,
  I want to perform a CRUD action on the locations resource

@tag5
  Scenario: Post data to locations table
    Given I reset the data by deleting id 9 in the dynamoDB table locations
    When I post the json locations_body to the resource locations
    Then I receive a status code 200 in response
    And I can retrieve data for id 9 in the dynamoDB table

@tag6
  Scenario: Add data to locations table
    Given I setup the data by inserting from file healthcareservices_body into the dynamoDB table healthcare_services
    When I delete data for id 9 from the resource healthcare_services
    Then data for id 9 in the dynamoDB table has been deleted


