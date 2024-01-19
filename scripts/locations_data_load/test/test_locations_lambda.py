import pandas as pd

from locations_lambda import read_ods_api, update_records
from locations_lambda import write_to_dynamodb, data_exists
from locations_lambda import get_headers, get_api_token
from locations_lambda import get_ssm, lambda_handler
from locations_lambda import fetch_organizations, fetch_y_organizations
from locations_lambda import capitalize_line, capitalize_address_item
from locations_lambda import process_organizations, read_excel_values

import unittest
from unittest.mock import patch, MagicMock, Mock


class TestLambdaHandler(unittest.TestCase):
    @patch("locations_lambda.fetch_organizations")
    @patch("locations_lambda.fetch_y_organizations")
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
    @patch("locations_lambda.boto3.resource")
    def test_update_records(self, mock_dynamodb_resource):
        # Mock DynamoDB resource and tables
        mock_dynamodb = mock_dynamodb_resource.return_value
        mock_org_table = Mock()
        mock_locations_table = Mock()
        mock_dynamodb.Table.side_effect = (
            lambda table_name: mock_org_table
            if table_name == "organisations"
            else mock_locations_table
        )

        # Mock DynamoDB scan responses
        mock_org_response = {
            "Items": [{"id": "org_id_1", "identifier": {"value": "123"}}]
        }
        mock_locations_response = {
            "Items": [
                {"id": "loc_id_1", "managingOrganization": "", "lookup_field": "123"}
            ]
        }
        mock_org_table.scan.return_value = mock_org_response
        mock_locations_table.scan.return_value = mock_locations_response

        # Call the function
        update_records()

        # Assert that update_item was called with the correct arguments
        mock_locations_table.update_item.assert_called_once_with(
            Key={"id": "loc_id_1"},
            UpdateExpression="SET managingOrganization = :val",
            ExpressionAttributeValues={":val": "org_id_1"},
        )


class TestReadODSAPI(unittest.TestCase):
    @patch("locations_lambda.requests.get")
    def test_read_ods_api_success(self, mock_requests_get):
        params = {"param1": "value1", "param2": "value2"}
        # Mocking get_api_token to return a dummy token
        headers = {"Authorization": "Bearer dummy_token"}
        # Mocking requests.get to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "dummy_data"}
        mock_requests_get.return_value = mock_response
        # Call the function with dummy parameters
        result = read_ods_api("dummy_api_endpoint", headers, params)

        # Assert that requests.get was called with the expected arguments
        mock_requests_get.assert_called_once_with(
            "dummy_api_endpoint",
            headers={"Authorization": "Bearer dummy_token"},
            params={"param1": "value1", "param2": "value2"},
        )
        # Assert that the result is as expected
        self.assertEqual(result, {"data": "dummy_data"})

    @patch("locations_lambda.requests.get")
    def test_read_ods_api_failure(self, mock_requests_get):
        params = {"param1": "value1", "param2": "value2"}
        headers = {"Authorization": "Bearer dummy_token"}

        # Mocking requests.get to return a failed response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_requests_get.return_value = mock_response

        # Call the function with dummy parameters
        result = read_ods_api("dummy_api_endpoint", headers, params)

        # Assert that requests.get was called with the expected arguments
        mock_requests_get.assert_called_once_with(
            "dummy_api_endpoint",
            headers={"Authorization": "Bearer dummy_token"},
            params={"param1": "value1", "param2": "value2"},
        )

        # Assert that the result is None in case of failure
        self.assertIsNone(result)


class TestWriteToDynamoDB(unittest.TestCase):
    @patch("locations_lambda.boto3.resource")
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
            "locations_lambda.data_exists", return_value=False
        ) as mock_data_exists:
            # Mock update_records function
            with patch("locations_lambda.update_records") as mock_update_records:
                # Call the function to test
                write_to_dynamodb("test_table", processed_data)

                # Assert that data_exists was called for each item in processed_data
                mock_data_exists.assert_any_call(mock_table, "value1")
                mock_data_exists.assert_any_call(mock_table, "value2")

                # Assert that put_item was called for each item where data doesn't exist
                mock_table.put_item.assert_called_with(Item=processed_data[1])
                mock_update_records.assert_called_once()

    @patch("locations_lambda.boto3.resource")
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


class TestSsmGetTokenGetHeaders(unittest.TestCase):
    @patch("locations_lambda.boto3.client")
    def test_get_ssm(self, mock_boto3_client):
        # Mocking boto3.client to avoid actual AWS calls
        mock_ssm_client = MagicMock()
        mock_boto3_client.return_value = mock_ssm_client

        # Mocking the response of get_parameter
        parameter_value = "mocked_value"
        mock_ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": parameter_value}
        }

        # Call the function with a mock parameter name
        result = get_ssm("mocked_parameter_name")

        # Assert that the mocked values were used and the function behaves as expected
        mock_boto3_client.assert_called_once_with("ssm")
        mock_ssm_client.get_parameter.assert_called_once_with(
            Name="mocked_parameter_name", WithDecryption=True
        )
        self.assertEqual(result, parameter_value)

    @patch("locations_lambda.get_ssm")
    @patch("locations_lambda.requests.post")
    def test_get_api_token(self, mock_post, mock_get_ssm):
        # Mocking the SSM calls
        mock_get_ssm.side_effect = lambda x: f"mocked_ssm_value{x}"

        # Mocking the response of the requests.post call
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "mocked_access_token"}
        mock_post.return_value = mock_response

        # Call the function
        result = get_api_token()

        # Assert that the mocked values were used and the function behaves as expected
        mock_post.assert_called_once_with(
            url="mocked_ssm_value/data/api/lambda/ods/domain"
            "//authorisation/auth/realms/terminology/protocol/openid-connect/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "Keep-alive",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": "mocked_ssm_value/data/api/lambda/client_id",
                "client_secret": "mocked_ssm_value/data/api/lambda/client_secret",
            },
        )
        self.assertEqual(result, "mocked_access_token")

    @patch("locations_lambda.get_api_token")
    def test_get_headers(self, mock_get_api_token):
        # Mocking the get_api_token call
        mock_get_api_token.return_value = "mocked_access_token"

        # Call the function
        result = get_headers()

        # Assert that the mocked values were used and the function behaves as expected
        mock_get_api_token.assert_called_once()
        self.assertEqual(result, {"Authorization": "Bearer mocked_access_token"})


class TestCapitalizeLine(unittest.TestCase):
    def test_capitalize_line(self):
        result = capitalize_line("hello world")
        self.assertEqual(result, "Hello World")


class TestCapitalizeAddressItem(unittest.TestCase):
    def test_capitalize_address_item(self):
        address_item = {
            "line": ["123 main street", "apt 4"],
            "city": "example city",
            "district": "example district",
            "country": "example country",
            "postalCode": "12345",
            "extension": {"key": "value"},
        }

        result = capitalize_address_item(address_item)

        expected_result = {
            "line": ["123 Main Street", "Apt 4"],
            "city": "Example City",
            "district": "Example District",
            "country": "Example Country",
            "postalCode": "12345",
        }

        self.assertEqual(result, expected_result)


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
        with patch("locations_lambda.uuid") as mock_uuid, patch(
            "locations_lambda.datetime"
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


class TestReadExcelValues(unittest.TestCase):
    @patch("pandas.read_excel")
    def test_read_excel_values(self, mock_read_excel):
        # Mocking pandas.read_excel
        mock_excel_data = pd.DataFrame({"ODS_Codes": ["123", "456"]})
        mock_read_excel.return_value = mock_excel_data

        # Call the function to test
        result = read_excel_values("fake_file_path.xlsx")

        # Assertions
        mock_read_excel.assert_called_once_with("fake_file_path.xlsx")

        expected_params = [
            {
                "primary-organization": "123",
                "_include": [
                    "OrganizationAffiliation:primary-organization",
                    "OrganizationAffiliation:participating-organization",
                ],
            },
            {
                "primary-organization": "456",
                "_include": [
                    "OrganizationAffiliation:primary-organization",
                    "OrganizationAffiliation:participating-organization",
                ],
            },
        ]
        self.assertEqual(result, expected_params)


class TestFetchOrganizations(unittest.TestCase):
    @patch("locations_lambda.get_ssm")
    @patch("locations_lambda.get_headers")
    @patch("locations_lambda.read_excel_values")
    @patch("locations_lambda.read_ods_api")
    @patch("locations_lambda.process_organizations")
    @patch("locations_lambda.write_to_dynamodb")
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
        mock_read_excel_values.assert_called_once_with("./ODS_Codes.xlsx")
        mock_read_ods_api.assert_called_with(
            "mocked_api_url/fhir/OrganizationAffiliation?active=true",
            {"Authorization": "Bearer token"},
            params="456",
        )
        mock_process_organizations.assert_called_once_with(mock_response_data["entry"])
        mock_write_to_dynamodb.assert_called_once_with(
            "locations", mock_process_organizations.return_value
        )

    @patch("locations_lambda.get_ssm")
    @patch("locations_lambda.get_headers")
    @patch("locations_lambda.read_ods_api")
    @patch("locations_lambda.process_organizations")
    @patch("locations_lambda.write_to_dynamodb")
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
