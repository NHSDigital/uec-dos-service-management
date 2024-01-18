@organisation_affiliations @pipeline_tests
Feature: organisation_affiliations
  As a user,
  I want to perform a CRUD action on the organisation_affiliations resource


  Scenario: Basic get request for organisation_affiliations
    Given I setup the data by inserting from file organisation_affiliations_body into the dynamoDB table organisation_affiliations
    When I request data for id=3188721443926156 from organisation_affiliations
    Then I receive a status code 200 in response
    And I receive data for id 3188721443926156 in the response


  Scenario: Basic post request for organisation_affiliations
    Given I reset the data by deleting id 3188721443926156 in the dynamoDB table organisation_affiliations
    When I post the json organisation_affiliations_body to the resource organisation_affiliations
    Then I receive a status code 200 in response
    And I can retrieve data for id 3188721443926156 in the dynamoDB table


  Scenario: Basic delete request for organisation_affiliations
    Given I setup the data by inserting from file organisation_affiliations_body into the dynamoDB table organisation_affiliations
    When I delete data for id 3188721443926156 from the resource organisation_affiliations
    Then data for id 3188721443926156 in the dynamoDB table has been deleted


