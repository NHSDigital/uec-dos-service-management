@process_csv @pipeline_tests
Feature: process_csv
  As a user,
  I want to be able to process a csv and read it's data

  Scenario: Assert row count
    Given I have the following csv file data_csv I have 5 rows

  Scenario: Assert column count
    Given I have the following csv file data_csv I have 3 columns

  Scenario: Assert file exists
    Given I have the following csv file data_csv, I can assert that the file exists

  Scenario: Assert file headers
    Given I have the following csv file data_csv I have the correct headers

  Scenario: Assert cell value
    Given I have the following csv file data_csv I can assert the correct value in a cell





