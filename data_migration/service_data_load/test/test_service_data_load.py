from data_migration.service_data_load.service_data_load import (
    read_s3_file,
    common_schema,
    write_to_dynamodb,
    update_services_providedby,
    update_services_location,
)
import unittest
from unittest.mock import Mock, patch, MagicMock


class TestAll(unittest.TestCase):
    @patch("data_migration.service_data_load.service_data_load.os.getenv")
    @patch("data_migration.service_data_load.service_data_load.boto3.resource")
    @patch("data_migration.service_data_load.service_data_load.pd.read_excel")
    def test_read_s3_file(self, mock_read_excel, mock_boto3_resource, mock_os_getenv):
        # Mocked data
        mock_bucket_name = "mock_bucket"
        mock_file = "Filtered_odscodes.xlsx"
        mock_excel_data = MagicMock()
        mock_grouped_data = MagicMock()

        # Set up mocks
        mock_os_getenv.return_value = mock_bucket_name
        mock_s3_resource = mock_boto3_resource.return_value
        mock_s3_object = mock_s3_resource.Object.return_value
        mock_s3_object.download_file.return_value = None
        mock_read_excel.return_value = mock_excel_data
        mock_excel_data.groupby.return_value = mock_grouped_data

        # Call the function
        result = read_s3_file()

        # Assertions
        self.assertEqual(result, mock_grouped_data)
        mock_os_getenv.assert_called_once_with("S3_DATA_BUCKET")
        mock_boto3_resource.assert_called_once_with("s3")
        mock_s3_resource.Object.assert_called_once_with(mock_bucket_name, mock_file)
        mock_s3_object.download_file.assert_called_once_with("/tmp/" + mock_file)
        mock_read_excel.assert_called_once_with("/tmp/" + mock_file)
        mock_excel_data.groupby.assert_called_once_with(["modified_odscode"])

    @patch(
        "data_migration.service_data_load.service_data_load.common_functions.generate_random_id"
    )
    @patch(
        "data_migration.service_data_load.service_data_load.common_functions.get_formatted_datetime"
    )
    def test_common_schema(self, mock_get_formatted_datetime, mock_generate_random_id):
        # Mock values and functions
        mock_generate_random_id.return_value = "mock_random_id"
        mock_get_formatted_datetime.return_value = "2024-01-24T12:00:00"

        # Call the function with sample inputs
        result = common_schema("value1", "value2", "name_value", "odscode", "day_list")

        # Assert the structure and values of the returned dictionary
        expected_result = {
            "id": "mock_random_id",
            "identifier": [
                {"type": "UID", "use": "oldDoS", "value": "value1"},
                {"type": "ID", "use": "oldDoS", "value": "value2"},
            ],
            "type": {
                "system": "https://terminology.hl7.org/CodeSystem/service-type",
                "code": "64",
                "display": "Pharmacy",
            },
            "active": "true",
            "name": "name_value",
            "odscode": "odscode",
            "createdDateTime": "2024-01-24T12:00:00",
            "createdBy": "Admin",
            "modifiedBy": "Admin",
            "modifiedDateTime": "2024-01-24T12:00:00",
            "providedBy": "",
            "location": "",
            "ServiceAvailability": "day_list",
        }
        self.assertEqual(result, expected_result)

        # Assert that generate_random_id and get_formatted_datetime were called
        mock_generate_random_id.assert_called_once()
        mock_get_formatted_datetime.assert_called_once()

    @patch("data_migration.service_data_load.service_data_load.boto3.resource")
    def test_write_to_dynamodb(self, mock_resource):
        # Mock the DynamoDB table and put_item method
        mock_table = Mock()
        mock_resource.return_value.Table.return_value = mock_table

        # Sample JSON data list
        json_data_list = [{"id": "1", "name": "Item 1"}, {"id": "2", "name": "Item 2"}]

        # Call the function with the sample table name and JSON data list
        write_to_dynamodb("table_name", json_data_list)

        # Assert that put_item was called twice with the correct arguments
        mock_table.put_item.assert_called_with(Item=json_data_list[1])
        self.assertEqual(mock_table.put_item.call_count, 2)

    @patch("data_migration.service_data_load.service_data_load.boto3")
    def test_update_services_providedby(self, mock_boto3):
        # Mock DynamoDB resource and tables
        mock_resource = MagicMock()
        mock_boto3.resource.return_value = mock_resource

        mock_healthcare_table = MagicMock()
        mock_organization_table = MagicMock()
        mock_resource.Table.side_effect = (
            lambda name: mock_healthcare_table
            if name == "healthcare_table_name"
            else mock_organization_table
        )

        # Mock response for organization table query
        mock_organization_table.query.return_value = {
            "Count": 1,
            "Items": [{"id": "org_id"}],
        }

        # Call the function to test
        update_services_providedby(
            "healthcare_table_name", [{"id": "1", "odscode": "123"}]
        )

        # Assert that query was called with correct arguments
        mock_organization_table.query.assert_called_once_with(
            KeyConditionExpression="id = :idvalue",
            FilterExpression="identifier.#val = :val",
            ExpressionAttributeNames={"#val": "value"},
            ExpressionAttributeValues={":val": "123", ":idvalue": "1"},
        )

        # Assert that update_item was called with correct arguments
        mock_healthcare_table.update_item.assert_called_once_with(
            Key={"id": "1"},
            UpdateExpression="SET providedBy = :val",
            ExpressionAttributeValues={":val": "org_id"},
        )

    @patch("data_migration.service_data_load.service_data_load.boto3")
    def test_update_services_location(self, mock_boto3):
        # Mock DynamoDB resource and tables
        mock_resource = MagicMock()
        mock_boto3.resource.return_value = mock_resource

        mock_healthcare_table = MagicMock()
        mock_locations_table = MagicMock()
        mock_resource.Table.side_effect = (
            lambda name: mock_healthcare_table
            if name == "healthcare_table_name"
            else mock_locations_table
        )

        # Mock response for organization table query
        mock_locations_table.query.return_value = {
            "Count": 1,
            "Items": [{"id": "location_id"}],
        }

        # Call the function to test
        update_services_location(
            "healthcare_table_name", [{"id": "1", "odscode": "123"}]
        )

        # Assert that query was called with correct arguments
        mock_locations_table.query.assert_called_once_with(
            KeyConditionExpression="id = :idvalue",
            FilterExpression="lookup_field = :val",
            ExpressionAttributeValues={":val": "123", ":idvalue": "1"},
        )

        # Assert that update_item was called with correct arguments
        mock_healthcare_table.update_item.assert_called_once_with(
            Key={"id": "1"},
            UpdateExpression="SET #location = :val",
            ExpressionAttributeNames={"#location": "location"},
            ExpressionAttributeValues={":val": "location_id"},
        )
