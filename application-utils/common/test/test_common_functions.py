import os
import unittest
from unittest.mock import patch, MagicMock
from unittest import mock
import datetime
import pandas as pd
from io import BytesIO

from common.common_functions import (
    get_table_name,
    get_ssm,
    get_api_token,
    get_headers,
    capitalize_address_item,
    capitalize_line,
    read_ods_api,
    generate_random_id,
    get_formatted_datetime,
    read_excel_values,
)


# Set Test variables
workspace_env_name = "WORKSPACE"
workspace_env_value = "DR-000"
workspace_env_default_value = ""
test_table_name = "TEST-TABLE"


def test_get_table_name_with_no_environment_var():
    # Test get_table_name method without WORKSPACE environment variable set
    table_name = get_table_name(test_table_name)
    assert table_name == test_table_name


def test_get_table_name_with_no_environment_var_empty_table_name():
    # Test get_table_name method without WORKSPACE environment variable set and empty table name
    table_name = get_table_name("")
    assert table_name == ""


@mock.patch.dict(os.environ, {workspace_env_name: workspace_env_default_value})
def test_get_table_name_with_environment_var_empty():
    # Test get_table_name method with WORKSPACE environment variable empty"
    table_name = get_table_name(test_table_name)
    assert table_name == test_table_name


@mock.patch.dict(os.environ, {workspace_env_name: workspace_env_value})
def test_get_table_name_with_environment_var_set():
    # Test get_table_name method with WORKSPACE environment variable set"
    table_name = get_table_name(test_table_name)
    assert table_name == test_table_name + "-" + workspace_env_value


@mock.patch.dict(os.environ, {workspace_env_name: workspace_env_value})
def test_get_table_name_with_environment_var_set_empty_table_name():
    # Test get_table_name method with WORKSPACE environment variable set with no table name set"
    table_name = get_table_name("")
    assert table_name == "-" + workspace_env_value


class TestSsmGetTokenGetHeaders(unittest.TestCase):
    @patch("common.common_functions.boto3.client")
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

    @patch("common.common_functions.get_ssm")
    @patch("common.common_functions.requests.post")
    def test_get_api_token(self, mock_post, mock_get_ssm):
        # Mocking the SSM calls
        mock_get_ssm.side_effect = lambda x: f"mocked_ssm_value{x}"

        # Mocking the response of the requests.post call
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "mocked_access_token"}
        mock_post.return_value = mock_response

        # Call the function
        result = get_api_token("/domain", "/user", "/secret")

        # Assert that the mocked values were used and the function behaves as expected
        mock_post.assert_called_once_with(
            url="mocked_ssm_value/domain"
            "//authorisation/auth/realms/terminology/protocol/openid-connect/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "Keep-alive",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": "mocked_ssm_value/user",
                "client_secret": "mocked_ssm_value/secret",
            },
        )
        self.assertEqual(result, "mocked_access_token")

    @patch("common.common_functions.get_api_token")
    def test_get_headers(self, mock_get_api_token):
        # Mocking the get_api_token call
        mock_get_api_token.return_value = "mocked_access_token"
        mocked_ssm_base_api_url = "url"
        mocked_ssm_param_id = "id"
        mocked_ssm_param_sec = "password"

        # Call the function
        result = get_headers(
            mocked_ssm_base_api_url, mocked_ssm_param_id, mocked_ssm_param_sec
        )

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


class TestReadODSAPI(unittest.TestCase):
    @patch("common.common_functions.requests.get")
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

    @patch("common.common_functions.requests.get")
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


class TestGenerateRandomId(unittest.TestCase):
    def test_generate_random_id_length(self):
        # Call the function to generate a random ID
        random_id = generate_random_id()

        # Assert that the length of the generated ID is 16
        self.assertEqual(len(random_id), 16)


class TestGetFormattedDatetime(unittest.TestCase):
    def test_get_formatted_datetime_format(self):
        # Call the function to get the formatted datetime
        formatted_datetime = get_formatted_datetime()

        # Define the expected format
        expected_format = "%d-%m-%Y %H:%M:%S"

        # Use try-except block to catch any exceptions raised by strptime
        try:
            # Try to parse the formatted datetime using the expected format
            datetime.datetime.strptime(formatted_datetime, expected_format)
        except ValueError:
            # If parsing fails, raise an AssertionError
            self.fail(
                f"Formatted datetime '{formatted_datetime}' does not match the expected format '{expected_format}'."
            )


class TestReadExcelValues(unittest.TestCase):
    @patch("common.common_functions.os.getenv")
    @patch("common.common_functions.boto3.client")
    def test_read_excel_values(self, mock_boto_client, mock_getenv):
        # Mocking environment variables
        mock_getenv.side_effect = lambda x: {
            "S3_DATA_BUCKET": "mocked_bucket",
            "ODS_CODES_XLSX_FILE": "mocked_file.xlsx",
        }.get(x)

        # Mocking boto3.client('s3') and s3.get_object
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client
        mock_excel_data = pd.DataFrame({"ODS_Codes": ["F123", "P456"]}, dtype=str)
        mock_body = BytesIO()
        mock_excel_data.to_excel(mock_body, index=False)
        mock_body.seek(0)
        mock_s3_client.get_object.return_value = {"Body": mock_body}

        # Call the function to test
        result = read_excel_values()

        # Assertions
        mock_getenv.assert_called_with("ODS_CODES_XLSX_FILE")
        mock_boto_client.assert_called_once_with("s3")
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="mocked_bucket", Key="mocked_file.xlsx"
        )

        # Convert result to DataFrame for comparison
        expected_params = [
            {
                "primary-organization": "F123",
                "_include": [
                    "OrganizationAffiliation:primary-organization",
                    "OrganizationAffiliation:participating-organization",
                ],
            },
            {
                "primary-organization": "P456",
                "_include": [
                    "OrganizationAffiliation:primary-organization",
                    "OrganizationAffiliation:participating-organization",
                ],
            },
        ]
        expected_params_df = pd.DataFrame(expected_params)

        self.assertEqual(type(result[0]["primary-organization"]), str)

        pd.testing.assert_frame_equal(pd.DataFrame(result), expected_params_df)
