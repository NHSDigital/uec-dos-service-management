from scripts.org_data_load.deploy.org_data_load import (
    lambda_handler,
    get_ssm,
    get_api_token,
    get_headers,
    capitalize_address_item,
    capitalize_line,
    read_excel_values,
    read_ods_api,
    write_to_dynamodb,
    generate_random_id,
    get_formatted_datetime,
    process_organization,
    process_pharmacy,
    process_non_pharmacy,
    process_organizations,
    process_type,
    data_exists,
    update_records,
    fetch_organizations,
    get_table_name,
)

import os
import unittest
from unittest.mock import patch, MagicMock, Mock
from unittest import mock
import pandas as pd
import datetime


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


class TestLambdaHandler(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.fetch_organizations")
    def test_lambda_handler(self, mock_fetch_organizations):
        # Set up mock event and context
        event = {"some_key": "some_value"}
        context = MagicMock()

        # Execute the lambda_handler function
        lambda_handler(event, context)

        # Assertions
        mock_fetch_organizations.assert_called_once()


class TestSsmGetTokenGetHeaders(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.boto3.client")
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

    @patch("scripts.org_data_load.deploy.org_data_load.get_ssm")
    @patch("scripts.org_data_load.deploy.org_data_load.requests.post")
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

    @patch("scripts.org_data_load.deploy.org_data_load.get_api_token")
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


class TestReadODSAPI(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.requests.get")
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

    @patch("scripts.org_data_load.deploy.org_data_load.requests.get")
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
    @patch("scripts.org_data_load.deploy.org_data_load.boto3.resource")
    @patch("scripts.org_data_load.deploy.org_data_load.update_records")
    @patch("scripts.org_data_load.deploy.org_data_load.data_exists")
    def test_write_to_dynamodb_with_new_data(
        self, mock_data_exists, mock_update_records, mock_dynamodb_resource
    ):
        # Mock DynamoDB table and responses
        mock_table = Mock()
        mock_dynamodb_resource.return_value.Table.return_value = mock_table
        mock_data_exists.return_value = False

        # Call the function
        write_to_dynamodb(
            "organizations", [{"identifier": {"value": "123"}, "other_key": "value"}]
        )

        # Assert that put_item was called for the new data
        mock_table.put_item.assert_called_once()

        # Assert that update_records was called
        mock_update_records.assert_called_once_with(mock_table)

    @patch("scripts.org_data_load.deploy.org_data_load.boto3.resource")
    @patch("scripts.org_data_load.deploy.org_data_load.update_records")
    @patch("scripts.org_data_load.deploy.org_data_load.data_exists")
    def test_write_to_dynamodb_with_existing_data(
        self, mock_data_exists, mock_update_records, mock_dynamodb_resource
    ):
        # Mock DynamoDB table and responses
        mock_table = Mock()
        mock_dynamodb_resource.return_value.Table.return_value = mock_table
        mock_data_exists.return_value = True

        # Call the function
        write_to_dynamodb(
            "organizations", [{"identifier": {"value": "123"}, "other_key": "value"}]
        )

        # Assert that put_item was not called for existing data
        mock_table.put_item.assert_not_called()

        # Assert that update_records was called
        mock_update_records.assert_called_once_with(mock_table)

    @patch("scripts.org_data_load.deploy.org_data_load.boto3.resource")
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

    @patch("scripts.org_data_load.deploy.org_data_load.print")
    @patch("scripts.org_data_load.deploy.org_data_load.boto3.resource")
    def test_update_records_with_existing_data(self, mock_print, mock_table):
        # Mock data with existing data in the DynamoDB table
        mock_table.scan.return_value = {
            "Items": [
                {"lookup_field": "123", "id": "456", "identifier": {"value": "789"}}
            ]
        }

        # Call the function to update records
        update_records(mock_table)

        # Assert that the update_item method was called with the correct parameters
        mock_table.update_item.assert_called_once_with(
            Key={"id": "456"},
            UpdateExpression="SET partOf = :val",
            ExpressionAttributeValues={":val": "456"},
        )


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


class TestProcessOrganization(unittest.TestCase):
    def test_process_organization_with_pharmacy_headquarter(self):
        # Mock data with a pharmacy headquarter organization
        organizations = [
            {
                "resource": {
                    "resourceType": "Organization",
                    "type": [{"coding": [{"display": "PHARMACY HEADQUARTER"}]}],
                }
            }
        ]

        # Call the function to process organizations
        result = process_organization(organizations)

        # Assert that the result is the pharmacy headquarter organization
        self.assertEqual(result, organizations[0]["resource"])

    def test_process_organization_without_pharmacy_headquarter(self):
        # Mock data without a pharmacy headquarter organization
        organizations = [
            {
                "resource": {
                    "resourceType": "Organization",
                    "type": [{"coding": [{"display": "SOME OTHER TYPE"}]}],
                }
            }
        ]

        # Call the function to process organizations
        result = process_organization(organizations)

        # Assert that the result is None since there's no pharmacy headquarter organization
        self.assertIsNone(result)


class TestProcessPharmacy(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.capitalize_address_item")
    @patch("scripts.org_data_load.deploy.org_data_load.generate_random_id")
    @patch("scripts.org_data_load.deploy.org_data_load.process_type")
    @patch("scripts.org_data_load.deploy.org_data_load.get_formatted_datetime")
    def test_process_pharmacy_with_ph_org(
        self,
        mock_get_formatted_datetime,
        mock_process_type,
        mock_generate_random_id,
        mock_capitalize_address_item,
    ):
        # Mock data with a pharmacy organization and a pharmacy headquarter organization
        org = {
            "resourceType": "Organization",
            "id": "org_id",
            "name": "Pharmacy Name",
            "type": "Some Type",
            "address": [{"street": "123 Main St", "city": "City", "state": "State"}],
        }
        ph_org = {"id": "ph_org_id"}

        # Mock the functions and methods used within process_pharmacy
        mock_capitalize_address_item.return_value = {
            "street": "123 Main St",
            "city": "City",
            "state": "State",
        }
        mock_generate_random_id.return_value = "generated_id"
        mock_process_type.return_value = "Processed Type"
        mock_get_formatted_datetime.return_value = "formatted_datetime"

        # Call the function to process pharmacy
        result = process_pharmacy(org, ph_org)

        # Assert that the result has the expected attributes based on the mock data
        self.maxDiff = None
        self.assertEqual(
            result,
            {
                "resourceType": "Organization",
                "id": "generated_id",
                "identifier": {"use": "secondary", "type": "ODS", "value": "org_id"},
                "active": "true",
                "type": "Processed Type",
                "name": "Pharmacy Name",
                "Address": [
                    {"street": "123 Main St", "city": "City", "state": "State"}
                ],
                "createdDateTime": "formatted_datetime",
                "partOf": "",
                "lookup_field": "ph_org_id",
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": "formatted_datetime",
            },
        )

    @patch("scripts.org_data_load.deploy.org_data_load.capitalize_address_item")
    @patch("scripts.org_data_load.deploy.org_data_load.generate_random_id")
    @patch("scripts.org_data_load.deploy.org_data_load.process_type")
    @patch("scripts.org_data_load.deploy.org_data_load.get_formatted_datetime")
    def test_process_pharmacy_without_ph_org(
        self,
        mock_get_formatted_datetime,
        mock_process_type,
        mock_generate_random_id,
        mock_capitalize_address_item,
    ):
        # Mock data with a pharmacy organization but without a pharmacy headquarter organization
        org = {
            "resourceType": "Organization",
            "id": "org_id",
            "name": "Pharmacy Name",
            "type": "Some Type",
            "address": [{"street": "123 Main St", "city": "City", "state": "State"}],
        }
        ph_org = None

        # Mock the functions and methods used within process_pharmacy
        mock_capitalize_address_item.return_value = {
            "street": "123 Main St",
            "city": "City",
            "state": "State",
        }
        mock_generate_random_id.return_value = "generated_id"
        mock_process_type.return_value = "Processed Type"
        mock_get_formatted_datetime.return_value = "formatted_datetime"

        # Call the function to process pharmacy
        result = process_pharmacy(org, ph_org)

        # Assert that the result has the expected attributes based on the mock data
        self.assertEqual(
            result,
            {
                "resourceType": "Organization",
                "id": "generated_id",
                "identifier": {"use": "secondary", "type": "ODS", "value": "org_id"},
                "active": "true",
                "type": "Processed Type",
                "name": "Pharmacy Name",
                "Address": [
                    {"street": "123 Main St", "city": "City", "state": "State"}
                ],
                "createdDateTime": "formatted_datetime",
                "partOf": "",
                "lookup_field": None,
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": "formatted_datetime",
            },
        )


class TestProcessNonPharmacy(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.capitalize_address_item")
    @patch("scripts.org_data_load.deploy.org_data_load.generate_random_id")
    @patch("scripts.org_data_load.deploy.org_data_load.process_type")
    @patch("scripts.org_data_load.deploy.org_data_load.get_formatted_datetime")
    def test_process_non_pharmacy(
        self,
        mock_get_formatted_datetime,
        mock_process_type,
        mock_generate_random_id,
        mock_capitalize_address_item,
    ):
        # Mock data for a non-pharmacy organization
        org = {
            "resourceType": "Organization",
            "id": "org_id",
            "name": "Non-Pharmacy Name",
            "type": "Some Type",
            "address": [{"street": "456 Second St", "city": "City", "state": "State"}],
        }

        # Mock the functions and methods used within process_non_pharmacy
        mock_capitalize_address_item.return_value = {
            "street": "456 Second St",
            "city": "City",
            "state": "State",
        }
        mock_generate_random_id.return_value = "generated_id"
        mock_process_type.return_value = "Processed Type"
        mock_get_formatted_datetime.return_value = "formatted_datetime"

        # Call the function to process non-pharmacy organization
        result = process_non_pharmacy(org)

        # Assert that the result has the expected attributes based on the mock data
        self.assertEqual(
            result,
            {
                "resourceType": "Organization",
                "id": "generated_id",
                "identifier": {"use": "secondary", "type": "ODS", "value": "org_id"},
                "active": "true",
                "type": "Processed Type",
                "name": "Non-Pharmacy Name",
                "Address": [
                    {"street": "456 Second St", "city": "City", "state": "State"}
                ],
                "createdDateTime": "formatted_datetime",
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": "formatted_datetime",
            },
        )


class TestProcessOrganizations(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.process_organization")
    @patch("scripts.org_data_load.deploy.org_data_load.process_pharmacy")
    @patch("scripts.org_data_load.deploy.org_data_load.process_non_pharmacy")
    def test_process_organizations(
        self,
        mock_process_non_pharmacy,
        mock_process_pharmacy,
        mock_process_organization,
    ):
        # Mock data with a pharmacy and a non-pharmacy organization
        organizations = [
            {
                "resource": {
                    "resourceType": "Organization",
                    "type": [{"coding": [{"display": "PHARMACY"}]}],
                }
            },
            {
                "resource": {
                    "resourceType": "Organization",
                    "type": [{"coding": [{"display": "Some Other Type"}]}],
                }
            },
        ]

        # Mock the functions used within process_organizations
        mock_process_organization.return_value = {"ph_org_attr": "pharmacy_attributes"}
        mock_process_pharmacy.return_value = {"processed_attr": "pharmacy_attributes"}
        mock_process_non_pharmacy.return_value = {
            "processed_attr": "non_pharmacy_attributes"
        }

        # Call the function to process organizations
        result = process_organizations(organizations)

        # Assert that the result has the expected processed attributes based on the mock data
        self.assertEqual(
            result,
            [
                {"processed_attr": "pharmacy_attributes"},
                {"processed_attr": "non_pharmacy_attributes"},
            ],
        )

        # Assert that process_organization was called with the correct arguments
        mock_process_organization.assert_called_once_with(organizations)

        # Assert that process_pharmacy was called with the correct arguments
        mock_process_pharmacy.assert_called_once_with(
            organizations[0]["resource"], {"ph_org_attr": "pharmacy_attributes"}
        )

        # Assert that process_non_pharmacy was called with the correct arguments
        mock_process_non_pharmacy.assert_called_once_with(organizations[1]["resource"])


class TestProcessType(unittest.TestCase):
    def test_process_type_with_valid_coding(self):
        # Mock data with valid coding information
        types = [
            {
                "coding": [
                    {"system": "https://ods-prototype/role", "display": "some_role"}
                ]
            }
        ]

        # Call the function to process types
        result = process_type(types)

        # Assert that the result is the title-cased display value from the coding
        self.assertEqual(result, "Some_Role")

    def test_process_type_with_invalid_coding(self):
        # Mock data with invalid coding information
        types = [{"coding": [{"system": "https://ods-prototype/role"}]}]

        # Call the function to process types
        result = process_type(types)

        # Assert that the result is the default value since the coding system is not the expected one
        self.assertEqual(result, "Default_Value")

    def test_process_type_with_empty_types(self):
        # Mock data with an empty list of types
        types = []

        # Call the function to process types
        result = process_type(types)

        # Assert that the result is None since there are no types to process
        self.assertIsNone(result)


class TestFetchOrganizations(unittest.TestCase):
    @patch("scripts.org_data_load.deploy.org_data_load.get_ssm")
    @patch("scripts.org_data_load.deploy.org_data_load.get_headers")
    @patch("scripts.org_data_load.deploy.org_data_load.read_excel_values")
    @patch("scripts.org_data_load.deploy.org_data_load.read_ods_api")
    @patch("scripts.org_data_load.deploy.org_data_load.process_organizations")
    @patch("scripts.org_data_load.deploy.org_data_load.write_to_dynamodb")
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
            "456",
        )
        mock_process_organizations.assert_called_once_with(mock_response_data["entry"])
        mock_write_to_dynamodb.assert_called_once_with(
            "organisations", mock_process_organizations.return_value
        )
