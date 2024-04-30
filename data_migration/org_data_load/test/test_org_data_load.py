from data_migration.org_data_load.org_data_load import (
    lambda_handler,
    write_to_dynamodb,
    process_organization,
    process_pharmacy,
    process_non_pharmacy,
    process_organizations,
    process_type,
    data_exists,
    update_records,
    fetch_organizations,
)

import unittest
from unittest.mock import patch, MagicMock, Mock


class TestLambdaHandler(unittest.TestCase):
    @patch("data_migration.org_data_load.org_data_load.fetch_organizations")
    def test_lambda_handler(self, mock_fetch_organizations):
        # Set up mock event and context
        event = {"some_key": "some_value"}
        context = MagicMock()

        # Execute the lambda_handler function
        lambda_handler(event, context)

        # Assertions
        mock_fetch_organizations.assert_called_once()


class TestWriteToDynamoDB(unittest.TestCase):
    @patch("data_migration.org_data_load.org_data_load.boto3.resource")
    @patch("data_migration.org_data_load.org_data_load.update_records")
    @patch("data_migration.org_data_load.org_data_load.data_exists")
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

    @patch("data_migration.org_data_load.org_data_load.boto3.resource")
    @patch("data_migration.org_data_load.org_data_load.update_records")
    @patch("data_migration.org_data_load.org_data_load.data_exists")
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

    @patch("data_migration.org_data_load.org_data_load.boto3.resource")
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

    @patch("data_migration.org_data_load.org_data_load.print")
    @patch("data_migration.org_data_load.org_data_load.boto3.resource")
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
                    "type": [{"coding": [{"display": "Some Type"}]}],
                }
            }
        ]

        # Call the function to process organizations
        result = process_organization(organizations)

        # Assert that the result is None since there's no pharmacy headquarter organization
        self.assertIsNone(result)


class TestProcessPharmacy(unittest.TestCase):
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.capitalize_address_item"
    )
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.generate_random_id"
    )
    @patch("data_migration.org_data_load.org_data_load.process_type")
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.get_formatted_datetime"
    )
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

    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.capitalize_address_item"
    )
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.generate_random_id"
    )
    @patch("data_migration.org_data_load.org_data_load.process_type")
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.get_formatted_datetime"
    )
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
                "partOf": "",
                "Address": [
                    {"street": "123 Main St", "city": "City", "state": "State"}
                ],
                "createdDateTime": "formatted_datetime",
                "createdBy": "Admin",
                "lookup_field": None,
                "modifiedBy": "Admin",
                "modifiedDateTime": "formatted_datetime",
            },
        )


class TestProcessNonPharmacy(unittest.TestCase):
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.capitalize_address_item"
    )
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.generate_random_id"
    )
    @patch("data_migration.org_data_load.org_data_load.process_type")
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.get_formatted_datetime"
    )
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
    @patch("data_migration.org_data_load.org_data_load.process_organization")
    @patch("data_migration.org_data_load.org_data_load.process_pharmacy")
    @patch("data_migration.org_data_load.org_data_load.process_non_pharmacy")
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
    @patch("data_migration.org_data_load.org_data_load.common_functions.get_ssm")
    @patch("data_migration.org_data_load.org_data_load.common_functions.get_headers")
    @patch(
        "data_migration.org_data_load.org_data_load.common_functions.read_excel_values"
    )
    @patch("data_migration.org_data_load.org_data_load.common_functions.read_ods_api")
    @patch("data_migration.org_data_load.org_data_load.process_organizations")
    @patch("data_migration.org_data_load.org_data_load.write_to_dynamodb")
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
            "organisations", mock_process_organizations.return_value
        )
