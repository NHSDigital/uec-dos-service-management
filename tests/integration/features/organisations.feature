@organisations @pipeline_tests
Feature: organisation
  As a user,
  I want to perform a CRUD action on the organisations resource


  Scenario: Basic get request for organisation_affiliations
    Given I setup the data by inserting from file organisation_body into the dynamoDB table organisations
    When I request data for id=3188721443926156 from organisations
    Then I receive a status code 200 in response
    And I receive data for id 3188721443926156 in the response


  Scenario: Basic post request for organisations
    Given I reset the data by deleting id 3188721443926156 in the dynamoDB table organisations
    When I post the json organisation_body to the resource organisations
    Then I receive a status code 200 in response
    And I can retrieve data for id 3188721443926156 in the dynamoDB table


  Scenario: Basic delete request for organisations
    Given I setup the data by inserting from file organisation_body into the dynamoDB table organisations
    When I delete data for id 3188721443926156 from the resource organisations
    Then data for id 3188721443926156 in the dynamoDB table has been deleted


