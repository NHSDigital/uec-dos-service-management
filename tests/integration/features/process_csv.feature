@process_csv @pipeline_tests
Feature: process_csv
  As a user,
  I want to be able to process a csv and read it's data


  Scenario: Process a csv from a given file
    Given I have the following csv file data_csv, I can retrieve the data within the file

  Scenario: Assert file exists
    Given I have the following csv file data_csv, I can assert that the file exists

  Scenario: Assert row count
    Given I have the following csv file data_csv, I can assert that the number of rows in the file is correct

  Scenario: Assert column count
    Given I have the following csv file data_csv, I can assert that the number of columns in the file is correct

  Scenario: Assert file headers
    Given I have the following csv file data_csv, I can assert that the headers in the file are correct

  Scenario: Assert cell value
    Given I have the csv file data_csv, I can assert file has the correct value in row 2 of the some value column




