@process_csv @pipeline_tests
Feature: process_csv
  As a user,
  I want to be able to process a csv and read it's data
Background:
  Given I have a csv file called data_csv

  Scenario: Assert row count
    Then the file contains 5 rows

  Scenario: Assert column count
    Then the file contains 3 columns

  Scenario: Assert file headers
    Then the file contains the correct headers ['test_case', 'some_value', 'some_other_value']

  Scenario: Assert cell value
    Then the file contains value 16 in row 2 column 1
