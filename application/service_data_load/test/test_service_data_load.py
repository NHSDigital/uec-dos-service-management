from application.service_data_load.service_data_load import (
    read_s3_file,
    common_schema,
    write_to_dynamodb,
    update_services_providedby,
    update_services_location,
    schema_mapping,
)
import unittest
from unittest.mock import Mock, patch, MagicMock


class TestAll(unittest.TestCase):
    @patch("application.service_data_load.service_data_load.os.getenv")
    @patch("application.service_data_load.service_data_load.boto3.client")
    @patch("application.service_data_load.service_data_load.pd.read_excel")
    def test_read_s3_file(self, mock_read_excel, mock_boto3_client, mock_getenv):
        # Mock data and environment variables
        mock_getenv.side_effect = lambda x: {"S3_DATA_BUCKET": "bucket"}.get(x)

        # Create a Mock object to simulate the behavior of the S3 response
        mock_excel_data = Mock()
        mock_boto3_client.return_value.get_object.return_value = mock_excel_data

        # Call the function to read S3 file
        read_s3_file()

        # Assert that the read_excel method was called with the correct parameters
        mock_read_excel.assert_called_once_with(mock_excel_data)

        # Assert that the environment variables were accessed correctly
        mock_getenv.assert_called_with("S3_DATA_BUCKET")
        mock_boto3_client.assert_called_with("s3")
        mock_boto3_client.return_value.get_object.assert_called_once_with(
            Bucket="bucket", Key="Filtered_odscodes.xlsx"
        )

    @patch(
        "application.service_data_load.service_data_load.common_functions.generate_random_id"
    )
    @patch(
        "application.service_data_load.service_data_load.common_functions.get_formatted_datetime"
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

    # @patch("application.service_data_load.service_data_load.common_schema")
    # def test_map_to_json_schema(self, mock_common_schema):
    #     # Mock the input row
    #     input_row = {
    #         "uid": "value1",
    #         "id": "value2",
    #         "dosrewrite_name": "name_value",
    #         "modified_odscode": "odscode",
    #     }

    #     # Call the function with the input row
    #     map_to_json_schema(input_row)

    #     # Assert that common_schema was called with the correct arguments
    #     mock_common_schema.assert_called_once_with(
    #         "value1", "value2", "name_value", "odscode"
    #     )

    # @patch("application.service_data_load.service_data_load.common_schema")
    # def test_map_to_json_schema2(self, mock_common_schema):
    #     # Mock the input parameters
    #     duplicate_rows = Mock()
    #     duplicate_rows.iterrows.return_value = [
    #         (0, {"id": "id1", "uid": "uid1"}),
    #         (1, {"id": "id2", "uid": "uid2"}),
    #     ]
    #     groupkey = "groupkey_value"

    #     # Call the function with the input parameters
    #     map_to_json_schema2(duplicate_rows, groupkey)

    #     # Assert that common_schema was called with the correct arguments
    #     mock_common_schema.assert_called_once_with(
    #         ["id1", "id2"],
    #         ["uid1", "uid2"],
    #         "Community Pharmacy Consultation Service",
    #         "groupkey_value",
    #     )

    @patch("application.service_data_load.service_data_load.boto3.resource")
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

    @patch("application.service_data_load.service_data_load.boto3")
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

    @patch("application.service_data_load.service_data_load.boto3")
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

    @patch("application.service_data_load.service_data_load.read_s3_file")
    @patch("application.service_data_load.service_data_load.write_to_dynamodb")
    @patch("application.service_data_load.service_data_load.update_services_providedby")
    @patch("application.service_data_load.service_data_load.update_services_location")
    def test_schema_mapping(
        self,
        mock_update_services_location,
        mock_update_services_providedby,
        mock_write_to_dynamodb,
        mock_read_s3_file,
    ):
        # Mocking dependencies
        mock_group = MagicMock()
        mock_groupkey = "mock_groupkey"
        mock_unique_rows = MagicMock()
        mock_duplicate_rows = MagicMock()
        mock_row = MagicMock()

        # Set up the mock to return an iterator with expected values
        mock_read_s3_file.return_value.groupby.return_value.__iter__.return_value = (
            iter([(mock_groupkey, mock_group)])
        )
        mock_group.__getitem__.side_effect = [mock_unique_rows, mock_duplicate_rows]

        # Set up the mock for unique_rows.iterrows() to return an iterator that doesn't raise StopIteration
        mock_unique_rows.iterrows.return_value = iter([(0, mock_row)])

        # Call the function to test
        schema_mapping()

        # Assertions
        mock_write_to_dynamodb.assert_called()
        mock_update_services_providedby.assert_called()
        mock_update_services_location.assert_called()
