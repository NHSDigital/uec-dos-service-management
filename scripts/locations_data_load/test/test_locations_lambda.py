import locations_lambda
from locations_lambda import read_ods_api, update_records
from locations_lambda import write_to_dynamodb, data_exists
from locations_lambda import get_headers, get_api_token
from locations_lambda import get_ssm, lambda_handler
from locations_lambda import fetch_organizations, fetch_y_organizations

import unittest
from unittest.mock import patch, MagicMock, Mock
import json


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
        mock_table = MagicMock()
        mock_table1 = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table
        mock_boto3_resource.return_value.Table.return_value = mock_table1
        # Mock scan response for existing data
        mock_table.scan.return_value = {
            "Items": [{"lookup_field": "value1", "other_field": "data1"}]
        }
        mock_table1.scan.return_value = {"Items": [{}]}
        # value=str(mock_table.scan.return_value.get("Items")["lookup_field"])
        # Test with existing data
        result = data_exists(mock_table, "value1")
        # Test with existing data
        result = data_exists(mock_table, "value1")
        self.assertTrue(result)

        # Test with non-existing data
        result1 = data_exists(mock_table1, "something")
        self.assertFalse(result1)


class TestSsmGetTokenGetHeaders(unittest.TestCase):
    @patch("locations_lambda.boto3.client")
    def test_get_ssm(self, mock_boto3_client):
        # Set up mock SSM client
        ssm_mock = MagicMock()
        ssm_mock.get_parameter.side_effect = [
            {"Parameter": {"Value": "mock_client_id"}},
            {"Parameter": {"Value": "mock_client_secret"}},
        ]
        mock_boto3_client.return_value = ssm_mock

        # Execute the function
        client_id, client_secret = get_ssm("mock_id", "mock_secret")

        # Assertions
        self.assertEqual(client_id, "mock_client_id")
        self.assertEqual(client_secret, "mock_client_secret")

    @patch("locations_lambda.requests.post")
    @patch(
        "locations_lambda.get_ssm",
        return_value=("mock_client_id", "mock_client_secret"),
    )
    def test_get_api_token(self, mock_get_ssm, mock_requests_post):
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "mock_access_token"}
        mock_requests_post.return_value = mock_response

        # Execute the function
        token = get_api_token()

        # Assertions
        self.assertEqual(token, "mock_access_token")

    @patch("locations_lambda.get_api_token", return_value="mock_access_token")
    def test_get_headers(self, mock_get_api_token):
        # Execute the function
        headers = get_headers()

        # Assertions
        expected_headers = {"Authorization": "Bearer mock_access_token"}
        self.assertEqual(headers, expected_headers)
        # Ensure get_api_token is called
        mock_get_api_token.assert_called_once()


class TestFetchOrganizations(unittest.TestCase):
    @patch("locations_lambda.read_excel_values")
    @patch("locations_lambda.get_headers")
    @patch("locations_lambda.read_ods_api")
    @patch("locations_lambda.process_organizations")
    @patch("locations_lambda.write_to_dynamodb")
    def test_fetch_organizations(
        self,
        mock_write_to_dynamodb,
        mock_process_organizations,
        mock_read_ods_api,
        mock_get_headers,
        mock_read_excel_values,
    ):
        # Set up mock data and responses
        odscode_params = [{"param1": "value1"}, {"param2": "value2"}]
        headers = {"Authorization": "Bearer mock_access_token"}
        response_data = {"entry": [{"org1": "data1"}, {"org2": "data2"}]}
        table_name = locations_lambda.dynamodb_table_name

        # Set up mock functions and their responses
        mock_read_excel_values.return_value = odscode_params
        mock_get_headers.return_value = headers
        mock_read_ods_api.return_value = response_data
        mock_process_organizations.return_value = processed_data = [
            {"processed_org1": "data1"},
            {"processed_org2": "data2"},
        ]

        # Execute the function
        fetch_organizations()

        # Assertions
        mock_read_excel_values.assert_called_once_with("./ODS_Codes.xlsx")
        mock_get_headers.assert_called_once()
        mock_read_ods_api.assert_called_with(
            "https://beta.ods.dc4h.link/fhir/OrganizationAffiliation?active=true",
            headers,
            params=odscode_params[1],
        )
        mock_process_organizations.assert_called_with(response_data["entry"])
        mock_write_to_dynamodb.assert_called_with(table_name, processed_data)

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
    ):
        # Set up mock data and responses
        headers = {"Authorization": "Bearer mock_access_token"}
        y_response_data = {"entry": [{"org_y1": "data1"}, {"org_y2": "data2"}]}
        table_name = locations_lambda.dynamodb_table_name

        # Set up mock functions and their responses
        mock_get_headers.return_value = headers
        mock_read_ods_api.return_value = y_response_data
        mock_process_organizations.return_value = processed_data_y = [
            {"processed_org_y1": "data1"},
            {"processed_org_y2": "data2"},
        ]

        # Execute the function
        fetch_y_organizations()

        # Assertions
        mock_get_headers.assert_called_once()
        mock_read_ods_api.assert_called_with(
            "https://beta.ods.dc4h.link/fhir/Organization?active=true",
            headers,
            params={"type": "RO209"},
        )
        mock_process_organizations.assert_called_with(y_response_data["entry"])
        mock_write_to_dynamodb.assert_called_with(table_name, processed_data_y)


def read_json():
    json_file_dir = "./scripts/locations_data_load/test/events/response.json"
    read = open(json_file_dir)
    data = json.load(read)
    return data


def test_process_organizations():
    data = read_json().get("entry", [])
    processed_data = locations_lambda.process_organizations(data)
    assert processed_data != ""


address_item = {
    "line": ["CERTAIN", "PHARMACY", "ADDRESS"],
    "city": "CITY",
    "district": "CERTAIN DISTRICT",
    "postalCode": "A11 11AE",
    "country": "ENGLAND",
    "not_extension": "EXTENSION",
}


def test_capitalize_address_item():
    response = locations_lambda.capitalize_address_item(address_item)
    for key, value in address_item.items():  #
        if key == "line" and isinstance(value, list):
            assert response[key] == [
                locations_lambda.capitalize_line(line) for line in value
            ]
        elif key in ["city", "district", "country"]:
            assert response[key] == value.title()
        elif key == "postalCode":
            assert response[key] == value
        elif key != "extension":
            assert response[key] == value


def test_read_excel_values():
    file_path = "./scripts/locations_data_load/test/events/dummy_ods_codes.xlsx"
    read_excel_response = [
        {
            "primary-organization": "FR999",
            "_include": [
                "OrganizationAffiliation:primary-organization",
                "OrganizationAffiliation:participating-organization",
            ],
        }
    ]
    response = locations_lambda.read_excel_values(file_path)
    assert response == read_excel_response
