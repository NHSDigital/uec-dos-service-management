@s3_interaction @pipeline_tests
Feature: S3 Interaction
  As a user,
  I want to be able to interact with an S3 bucket


  Scenario: Upload file to S3 bucket
    Given I want to upload the file test_file to the s3 bucket nhse-uec-cm-domain-test-bucket-dev-dr-859

  Scenario: Get file from S3 bucket
    Given I want to retreive the file test_file from the s3 bucket nhse-uec-cm-domain-test-bucket-dev-dr-859

  Scenario: Delete file from S3 bucket
    Given I want to delete the file test_file from the s3 bucket nhse-uec-cm-domain-test-bucket-dev-dr-859
