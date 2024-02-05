from application.locations_data_load.locations_lambda import (
    update_records,
    write_to_dynamodb,
    data_exists,
    lambda_handler,
    fetch_organizations,
    fetch_y_organizations,
    process_organizations,
)

import unittest
from unittest.mock import patch, MagicMock, Mock


class TestLambdaHandler(unittest.TestCase):
    @patch("application.locations_data_load.locations_lambda.fetch_organizations")
    @patch("application.locations_data_load.locations_lambda.fetch_y_organizations")
    def test_lambda_handler(self, mock_fetch_y_organizations, mock_fetch_organizations):
        # Set up mock event and context
        event = {"some_key": "some_value"}
        context = MagicMock()

        # Execute the lambda_handler function
        lambda_handler(event, context)

        # Assertions
        mock_fetch_organizations.assert_called_once()
        mock_fetch_y_organizations.assert_called_once()


class TestUpdateRecords(unittest.TestCase):
    @patch("application.locations_data_load.locations_lambda.boto3.resource")
    @patch(
        "application.locations_data_load.locations_lambda.workspace_locations_table_name",
        "locations_table_name",
    )
    @patch(
        "application.locations_data_load.locations_lambda.organisations_table_name",
        "organisations_table_name",
    )
    def test_update_records_with_existing_data(self, mock_resource):
        # Mock data with existing data in the DynamoDB tables
        mock_org_table = Mock()
        mock_locations_table = Mock()
        mock_resource.return_value.Table.side_effect = [
            mock_org_table,
            mock_locations_table,
        ]

        mock_org_response = {
            "Items": [{"identifier": {"value": "123"}, "id": "org_id"}]
        }
        mock_locations_response = {
            "Items": [
                {
                    "lookup_field": "123",
                    "id": "locations_id",
                    "managingOrganization": "",
                }
            ]
        }
        mock_org_table.scan.return_value = mock_org_response
        mock_locations_table.scan.return_value = mock_locations_response

        # Call the function to update records
        update_records()

        # Assert that the update_item method was called with the correct parameters
        mock_locations_table.update_item.assert_called_once_with(
            Key={"id": "locations_id"},
            UpdateExpression="SET managingOrganization = :val",
            ExpressionAttributeValues={":val": "org_id"},
        )


class TestWriteToDynamoDB(unittest.TestCase):
    @patch("application.locations_data_load.locations_lambda.boto3.resource")
    def test_write_to_dynamodb(self, mock_boto3_resource):
        # Mock DynamoDB resource
        mock_table = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table

        # Mock data for testing
        processed_data = [
            {"lookup_field": "value1", "other_field": "data1"},
            {"lookup_field": "value2", "other_field": "data2"},
        ]

        # Mock data_exists function
        with patch(
            "application.locations_data_load.locations_lambda.data_exists",
            return_value=False,
        ) as mock_data_exists:
            # Mock update_records function
            with patch(
                "application.locations_data_load.locations_lambda.update_records"
            ) as mock_update_records:
                # Call the function to test
                write_to_dynamodb("test_table", processed_data)

                # Assert that data_exists was called for each item in processed_data
                mock_data_exists.assert_any_call(mock_table, "value1")
                mock_data_exists.assert_any_call(mock_table, "value2")

                # Assert that put_item was called for each item where data doesn't exist
                mock_table.put_item.assert_called_with(Item=processed_data[1])
                mock_update_records.assert_called_once()

    @patch("application.locations_data_load.locations_lambda.boto3.resource")
    def test_data_exists(self, mock_boto3_resource):
        # Mock DynamoDB resource
        mock_table_true = MagicMock()
        mock_table_false = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table_true
        mock_boto3_resource.return_value.Table.return_value = mock_table_false
        # Mock scan response for existing data
        mock_table_true.scan.return_value = {
            "Items": [{"lookup_field": "value1", "other_field": "data1"}]
        }
        mock_table_false.scan.return_value = {"Items": []}
        # Test with existing data
        result = data_exists(mock_table_true, "value1")
        self.assertTrue(result)

        # Test with non-existing data
        result = data_exists(mock_table_false, "something")
        self.assertFalse(result)


class TestProcessOrganizations(unittest.TestCase):
    def test_process_organizations(self):
        data = [
            {
                "fullUrl": "dummy_url",
                "resource": {
                    "resourceType": "Organization",
                    "id": "123",
                    "name": "example org",
                    "address": [
                        {
                            "line": ["123 main street", "apt 4"],
                            "city": "example city",
                            "district": "example district",
                            "country": "example country",
                            "postalCode": "12345",
                            "extension": [
                                {
                                    "url": "dummy_url",
                                    "extension": [
                                        {
                                            "url": "type",
                                            "valueCodeableConcept": {
                                                "coding": [
                                                    {
                                                        "system": "dummy_url",
                                                        "code": "UPRN",
                                                        "display": "Unique Property Reference Number",
                                                    }
                                                ]
                                            },
                                        },
                                        {"url": "value", "valueString": "12345678901"},
                                    ],
                                }
                            ],
                        }
                    ],
                },
            }
        ]
        with patch(
            "application.locations_data_load.locations_lambda.uuid"
        ) as mock_uuid, patch(
            "application.locations_data_load.locations_lambda.datetime"
        ) as mock_datetime:
            mock_uuid.uuid4.return_value.int = 1234567890123456
            mock_datetime.datetime.now.return_value.strftime.return_value = (
                "01-01-2022 12:00:00"
            )

            result = process_organizations(data)

        expected_result = [
            {
                "id": "1234567890123456",
                "lookup_field": "123",
                "active": "true",
                "name": "Example Org",
                "Address": [
                    {
                        "line": ["123 Main Street", "Apt 4"],
                        "city": "Example City",
                        "district": "Example District",
                        "country": "Example Country",
                        "postalCode": "12345",
                    }
                ],
                "createdDateTime": "01-01-2022 12:00:00",
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": "01-01-2022 12:00:00",
                "UPRN": "12345678901",
                "position": {"longitude": "", "latitude": ""},
                "managingOrganization": "",
            }
        ]

        self.assertEqual(result, expected_result)


class TestFetchOrganizations(unittest.TestCase):
    @patch("application.locations_data_load.locations_lambda.common_functions.get_ssm")
    @patch(
        "application.locations_data_load.locations_lambda.common_functions.get_headers"
    )
    @patch(
        "application.locations_data_load.locations_lambda.common_functions.read_excel_values"
    )
    @patch(
        "application.locations_data_load.locations_lambda.common_functions.read_ods_api"
    )
    @patch("application.locations_data_load.locations_lambda.process_organizations")
    @patch("application.locations_data_load.locations_lambda.write_to_dynamodb")
    def test_fetch_organizations(
        self,
        mock_write_to_dynamodb,
        mock_process_organizations,
        mock_read_ods_api,
        mock_read_excel_values,
        mock_get_headers,
        mock_get_ssm,
    ):
        # Mocking necessary functions
        mock_get_ssm.return_value = "mocked_api_url"
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_read_excel_values.return_value = {"456"}
        mock_response_data = {
            "entry": [{"organization": "data1"}, {"organization": "data2"}]
        }
        mock_read_ods_api.return_value = mock_response_data

        # Call the function to test
        fetch_organizations()

        # Assertions
        mock_get_ssm.assert_called_once_with("/data/api/lambda/ods/domain")
        mock_get_headers.assert_called_once()
        mock_read_excel_values.assert_called_once()
        mock_read_ods_api.assert_called_with(
            "mocked_api_url/fhir/OrganizationAffiliation?active=true",
            {"Authorization": "Bearer token"},
            "456",
        )
        mock_process_organizations.assert_called_once_with(mock_response_data["entry"])
        mock_write_to_dynamodb.assert_called_once_with(
            "locations", mock_process_organizations.return_value
        )

    @patch("application.locations_data_load.locations_lambda.common_functions.get_ssm")
    @patch(
        "application.locations_data_load.locations_lambda.common_functions.get_headers"
    )
    @patch(
        "application.locations_data_load.locations_lambda.common_functions.read_ods_api"
    )
    @patch("application.locations_data_load.locations_lambda.process_organizations")
    @patch("application.locations_data_load.locations_lambda.write_to_dynamodb")
    def test_fetch_y_organizations(
        self,
        mock_write_to_dynamodb,
        mock_process_organizations,
        mock_read_ods_api,
        mock_get_headers,
        mock_get_ssm,
    ):
        # Mocking necessary functions
        mock_get_ssm.return_value = "mocked_api_url"
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response_data = {
            "entry": [{"organization": "data1"}, {"organization": "data2"}]
        }
        mock_read_ods_api.return_value = mock_response_data

        # Call the function to test
        fetch_y_organizations()

        # Assertions
        mock_get_ssm.assert_called_once_with("/data/api/lambda/ods/domain")
        mock_get_headers.assert_called_once()
        mock_read_ods_api.assert_called_with(
            "mocked_api_url/fhir/Organization?active=true",
            {"Authorization": "Bearer token"},
            params={"type": "RO209"},
        )
        mock_process_organizations.assert_called_once_with(mock_response_data["entry"])
        mock_write_to_dynamodb.assert_called_once_with(
            "locations", mock_process_organizations.return_value
        )
