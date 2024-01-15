import locations_lambda
from locations_lambda import read_ods_api

import unittest
from unittest.mock import patch, MagicMock
import boto3
import json
from moto import mock_ssm


class TestReadODSAPI(unittest.TestCase):
    @patch("locations_lambda.get_api_token")
    @patch("locations_lambda.requests.get")
    def test_read_ods_api_success(self, mock_requests_get, mock_get_api_token):
        params = {"param1": "value1", "param2": "value2"}
        # Mocking get_api_token to return a dummy token
        mock_get_api_token.return_value = "dummy_token"
        # Mocking requests.get to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "dummy_data"}
        mock_requests_get.return_value = mock_response
        # Call the function with dummy parameters
        result = read_ods_api("dummy_api_endpoint", params=params)

        # Assert that get_api_token was called once
        mock_get_api_token.assert_called_once()
        # Assert that requests.get was called with the expected arguments
        mock_requests_get.assert_called_once_with(
            "dummy_api_endpoint",
            headers={"Authorization": "Bearer dummy_token"},
            params={"param1": "value1", "param2": "value2"},
        )
        # Assert that the result is as expected
        self.assertEqual(result, {"data": "dummy_data"})

    @patch("locations_lambda.get_api_token")
    @patch("locations_lambda.requests.get")
    def test_read_ods_api_failure(self, mock_requests_get, mock_get_api_token):
        params = {"param1": "value1", "param2": "value2"}
        # Mocking get_api_token to return a dummy token
        mock_get_api_token.return_value = "dummy_token"

        # Mocking requests.get to return a failed response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_requests_get.return_value = mock_response

        # Call the function with dummy parameters
        result = read_ods_api("dummy_api_endpoint", params=params)

        # Assert that get_api_token was called once
        mock_get_api_token.assert_called_once()

        # Assert that requests.get was called with the expected arguments
        mock_requests_get.assert_called_once_with(
            "dummy_api_endpoint",
            headers={"Authorization": "Bearer dummy_token"},
            params={"param1": "value1", "param2": "value2"},
        )

        # Assert that the result is None in case of failure
        self.assertIsNone(result)


def read_json():
    json_file_dir = "./scripts/locations_data_load/test/events/response.json"
    read = open(json_file_dir)
    data = json.load(read)
    return data


def test_process_organizations():
    data = read_json()
    processed_data = locations_lambda.process_organizations(data)
    assert processed_data != ""


@mock_ssm
def test_get_ssm():
    parameter_names = ["/foo/id", "/foo/sec"]
    ssm = boto3.client("ssm")
    ssm.put_parameter(
        Name=parameter_names[0],
        Description="test ID",
        Value="id value",
        Type="String",
    )
    ssm.put_parameter(
        Name=parameter_names[1],
        Description="test sec",
        Value="sec value",
        Type="SecureString",
    )
    response = locations_lambda.get_ssm(parameter_names[0], parameter_names[1])
    assert response[0] == "id value"
    assert response[1] == "sec value"


def test_generate_random_id():
    response = locations_lambda.generate_random_id()
    assert len(response) == 16


def test_get_formatted_datetime():
    assert locations_lambda.get_formatted_datetime() != ""


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


# locations_lambda.data_exists
# locations_lambda.update_records
# locations_lambda.write_to_json
# locations_lambda.process_organizations
# locations_lambda.read_excel_values
