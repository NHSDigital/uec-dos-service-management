Feature: Open weather api
  As a user,
  I want to find the temperature at a location

@tag0
  Scenario: Basic temperature request
    Given I send a temperature request
    Then I receive a 200 status response
    And I will receive a status 200 response

@tag2
  Scenario: Addtional temperature request
    Given I send a temperature request
    Then I receive a 200 status response
    And I will receive a status 400 response

@tag3
  Scenario: Timezone is GMT
    Given I send a temperature request
    And I get a response for the timezone GMT
    And I get a response of 13.419998 for item longitude
