@healthcare_services @pipeline_tests
@critical
Feature: Healthcare Services
  As a user,
  I want to perform a CRUD action on the healthcare_services resource

  @allure.label.story:DR-572-BackendApplicationCRUD-HealthcareServicesManager
  Scenario: Basic get request for healthcare_services
    Given I setup the data by inserting from file healthcareservices_body into the dynamoDB table healthcare_services
    When I request data for id=9 from healthcare_services
    Then I receive a status code 200 in response
    And I receive data for id 9 in the response

  @allure.label.story:DR-572-BackendApplicationCRUD-HealthcareServicesManager
  Scenario: Basic post request for healthcare_services
    Given I reset the data by deleting id 9 in the dynamoDB table healthcare_services
    When I post the json healthcareservices_body to the resource healthcare_services
    Then I receive a status code 200 in response
    And I can retrieve data for id 9 in the dynamoDB table

  @allure.label.story:DR-572-BackendApplicationCRUD-HealthcareServicesManager
  Scenario: Basic delete request for healthcare_services
    Given I setup the data by inserting from file healthcareservices_body into the dynamoDB table healthcare_services
    When I delete data for id 9 from the resource healthcare_services
    Then data for id 9 in the dynamoDB table has been deleted

