@s3_interaction @pipeline_tests @Test
Feature: S3 Interaction
  As a user,
  I want to be able to interact with an S3 bucket
Background:
  Given I want to upload the file s3_data_csv to the s3 bucket


  Scenario: Get file from S3 bucket
    Then I can download the file s3_data_csv.csv from the s3 bucket
    And the file contains 4 rows


  Scenario: Delete file from S3 bucket
    Then I can delete the file s3_data_csv.csv from the s3 bucket
