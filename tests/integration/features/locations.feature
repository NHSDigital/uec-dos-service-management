Feature: location
  As a user,
  I want to perform a CRUD action on the locations resource

@tag5
  Scenario: Post data to locations table
    Given I reset the data by deleting id 1025655242481332 in the dynamoDB table locations
    When I post the json locations_body to the resource locations
    Then I receive a status code 200 in response
    And I can retrieve data for id 1025655242481332 in the dynamoDB table

@tag6
  Scenario: Add data to locations table
    Given I setup the data by inserting from file locations_body into the dynamoDB table locations
    When I delete data for id 1025655242481332 from the resource locations

