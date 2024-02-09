from application.organisation_affiliations_data_load.orgaffiliation_lambda import (
    lambda_handler,
    process_orgaffiliation,
    write_to_dynamodborgaffili,
    update_orgaffiliation_org,
    update_orgaffiliation_partiorg,
    fetch_orgaffiliation,
)

import unittest
from unittest.mock import patch, MagicMock, Mock
from boto3.dynamodb.conditions import Attr


class TestLambdaHandler(unittest.TestCase):
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.fetch_orgaffiliation"
    )
    def test_lambda_handler(self, mock_fetch_orgaffiliation):
        # Set up mock event and context
        event = {"some_key": "some_value"}
        context = MagicMock()

        # Execute the lambda_handler function
        lambda_handler(event, context)

        # Assertions
        mock_fetch_orgaffiliation.assert_called_once()


class TestUpdateRecords(unittest.TestCase):
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.boto3.resource"
    )
    def test_update_orgaffiliation_org(self, mock_boto3):
        # Mock data with existing data in the DynamoDB tables
        mock_dynamodb = mock_boto3.return_value
        mock_orgaffiliation_table = mock_dynamodb.Table.return_value
        mock_org_table = mock_dynamodb.Table.return_value

        table_name = "my_table"
        data = [
            {
                "lookup_field_Org": "123",
                "id": "organisations_id",
                "organization": "",
            }
        ]

        mock_scan_result = {
            "Count": 1,
            "Items": [{"identifier": {"value": "123"}, "id": "org_id"}],
        }
        mock_org_table.scan.return_value = mock_scan_result

        expected_update = {
            "Key": {"id": "organisations_id"},
            "UpdateExpression": "SET organization = :val",
            "ExpressionAttributeValues": {":val": "org_id"},
        }

        # Call the function to update records
        update_orgaffiliation_org(table_name, data)

        mock_org_table.scan.assert_called_once_with(
            FilterExpression=Attr("identifier.value").eq("123")
        )
        mock_orgaffiliation_table.update_item.assert_called_once_with(expected_update)


class TestUpdateRecordsParti(unittest.TestCase):
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.boto3.resource"
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.workspace_orgaffiliation_table_name",
        "orgaffiliation_table_name",
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.organisations_table_name",
        "organisations_table_name",
    )
    def update_orgaffiliation_partiorg(self, mock_resource):
        # Mock data with existing data in the DynamoDB tables
        mock_org_table = Mock()
        mock_orgaffiliation_table = Mock()
        mock_resource.return_value.Table.side_effect = [
            mock_org_table,
            mock_orgaffiliation_table,
        ]

        mock_org_response = {
            "Items": [{"identifier": {"value": "123"}, "id": "org_id"}]
        }
        mock_orgaffiliation_response = {
            "Items": [
                {
                    "lookup_field_parti": "123",
                    "id": "organisations_id",
                    "participatingOrganization": "",
                }
            ]
        }
        mock_org_table.scan.return_value = mock_org_response
        mock_orgaffiliation_table.scan.return_value = mock_orgaffiliation_response

        # Call the function to update records
        update_orgaffiliation_partiorg()

        # Assert that the update_item method was called with the correct parameters
        mock_orgaffiliation_table.update_item.assert_called_once_with(
            Key={"id": "organisations_id"},
            UpdateExpression="SET participatingOrganization = :val",
            ExpressionAttributeValues={":val": "org_id"},
        )


class TestWriteToDynamoDBOrgaffili(unittest.TestCase):
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.boto3.resource"
    )
    def test_write_to_dynamodborgaffili(self, mock_boto3_resource):
        # Mock DynamoDB resource
        mock_table = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table

        # Mock data for testing
        processed_data = [
            {"lookup_field": "value1", "other_field": "data1"},
            {"lookup_field": "value2", "other_field": "data2"},
        ]

        # Call the function to test
        write_to_dynamodborgaffili("test_table", processed_data)

        # Assert that put_item was called for each item where data doesn't exist
        mock_table.put_item.assert_called_with(Item=processed_data[1])


class TestProcessorgaffiliation(unittest.TestCase):
    def test_process_orgaffiliation(self):
        data = [
            {
                "fullUrl": "dummy_url",
                "resource": {
                    "resourceType": "OrganizationAffiliation",
                    "id": "FC999",
                    "active": "true",
                    "period": {"start": "2000-01-01"},
                    "organization": {
                        "reference": "Organization/FF999",
                        "identifier": {"system": "dummy_url", "value": "FF999"},
                    },
                    "participatingOrganization": {
                        "reference": "Organization/P0XX",
                        "identifier": {"system": "dummy_url", "value": "P0XX"},
                    },
                    "code": [
                        {
                            "coding": [
                                {
                                    "system": "dummy_url",
                                    "code": "XXX",
                                    "display": "IS OPERATED BY",
                                }
                            ]
                        }
                    ],
                },
            }
        ]
        with patch(
            "application.organisation_affiliations_data_load.orgaffiliation_lambda.common_functions.uuid"
        ) as mock_uuid, patch(
            "application.organisation_affiliations_data_load.orgaffiliation_lambda.common_functions.datetime"
        ) as mock_datetime:
            mock_uuid.uuid4.return_value.int = 1234567890123456
            mock_datetime.datetime.now.return_value.strftime.return_value = (
                "01-01-2022 12:00:00"
            )

            result = process_orgaffiliation(data)

        expected_result = [
            {
                "resourceType": "OrganizationAffiliation",
                "id": "1234567890123456",
                "identifier": {
                    "use": "secondary",
                    "type": "ODS Org. Affiliation id",
                    "value": "FC999",
                },
                "active": "true",
                "periodStart": "2000-01-01",
                "organization": "",
                "participatingOrganization": "",
                "lookup_field_Org": "FF999",
                "lookup_field_parti": "P0XX",
                "code": [
                    {
                        "coding": [
                            {
                                "system": "dummy_url",
                                "code": "XXX",
                                "display": "IS OPERATED BY",
                            }
                        ]
                    }
                ],
                "createdDateTime": "01-01-2022 12:00:00",
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": "01-01-2022 12:00:00",
            }
        ]

        self.assertEqual(result, expected_result)


class TestFetchOrgaffiliation(unittest.TestCase):
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.common_functions.get_ssm"
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.common_functions.get_headers"
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.common_functions.read_excel_values"
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.common_functions.read_ods_api"
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.process_orgaffiliation"
    )
    @patch(
        "application.organisation_affiliations_data_load.orgaffiliation_lambda.write_to_dynamodborgaffili"
    )
    def test_fetch_orgaffiliation(
        self,
        mock_write_to_dynamodborgaffili,
        mock_process_orgaffiliation,
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
        fetch_orgaffiliation()

        # Assertions
        mock_get_ssm.assert_called_once_with("/data/api/lambda/ods/domain")
        mock_get_headers.assert_called_once()
        mock_read_excel_values.assert_called_once()
        mock_read_ods_api.assert_called_with(
            "mocked_api_url/fhir/OrganizationAffiliation?active=true",
            {"Authorization": "Bearer token"},
            "456",
        )
        mock_process_orgaffiliation.assert_called_once_with(mock_response_data["entry"])
        mock_write_to_dynamodborgaffili.assert_called_once_with(
            "organisation_affiliations", mock_process_orgaffiliation.return_value
        )
