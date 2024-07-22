import unittest
import tempfile
import pandas as pd
from datetime import datetime
from database_populator import DatabasePopulator
from unittest.mock import patch, call


class TestDatabasePopulator(unittest.TestCase):
    @patch("boto3.client")
    @patch("boto3.resource")
    @patch("os.environ.get")
    def setUp(self, mock_get, mock_resource, mock_client):
        print(">>Setting up")
        try:
            mock_get.return_value = "False"
            self.db_populator = DatabasePopulator()
            if not self._testMethodName.startswith("test_logging"):
                self.patcher = patch.object(self.db_populator, "setup_logger")
                self.mock_setup_logger = self.patcher.start()
        except Exception as e:
            print(e)

    def tearDown(self):
        if hasattr(self, "patcher"):
            self.patcher.stop()

    def test_init(self):
        """
        Test that the testing attribute is set to False when
        the class is initialized.
        """
        print(">>Testing init")
        try:
            self.assertEqual(self.db_populator.testing, False)
        except Exception as e:
            print(e)

    def test_logging_file_path(self):
        """
        Test that the log file path starts with the temp directory path.
        """
        print(">>Testing log file path")
        try:
            temp_dir = tempfile.gettempdir()
            self.assertTrue(
                self.db_populator.log_file.startswith(temp_dir),
                "Log file path does not start with the temp directory path",
            )
        except Exception as e:
            print(e)

    @patch("os.path.exists")
    def test_logging_remove_old_log_file(self, mock_exists):
        """
        Test that remove_old_log_file returns False when
        there's no log file to remove.
        """
        print(">>Testing remove old log file")
        # Mock os.path.exists to always return False
        mock_exists.return_value = False
        result = self.db_populator.remove_old_log_file("non_existent_file.log")
        self.assertFalse(
            result,
        )

    @patch("logging.FileHandler")
    def test_logging_setup_logger(self, mock_file_handler):
        """
        Test that setup_logger creates a FileHandler with the log file path.
        """
        print(">>Testing setup logger")
        with patch("logging.getLogger"):
            self.db_populator.setup_logger()
            try:
                mock_file_handler.assert_called_once_with(self.db_populator.log_file)
            except AssertionError:
                print("FileHandler was not called with the correct " "log file path.")

    def test_logging_log(self):
        """
        Test that log calls the logger's info method with the message.
        """
        print(">>Testing log")
        with patch.object(self.db_populator.logger, "info") as mock_info:
            self.db_populator.log("Test message")
            try:
                mock_info.assert_called_once_with(" " + "Test message")
            except AssertionError:
                print(
                    "Logger's info method was not called with the correct " "message."
                )

    @patch.object(DatabasePopulator, "log")
    def test_log_failures(self, mock_log):
        """
        Test that log_failures logs the correct messages.
        """
        print(">>Testing log failures")
        # Insert some failure data
        self.db_populator.fails = {
            "table1": [
                {"Source Identifier": "id1", "Error": "error1"},
                {"Source Identifier": "id2", "Error": "error2"},
            ],
            "table2": [],
            "table3": [{"Source Identifier": "id3", "Error": "error3"}],
        }
        self.db_populator.maximum_insert_fails = 10
        self.db_populator.insert_fails = 3
        # Call the log_failures method
        self.db_populator.log_failures()
        # Check if the correct log messages were generated
        calls = [
            call("Failed to insert 2 items into table1", "Error"),
            call({"Source Identifier": "id1", "Error": "error1"}),
            call({"Source Identifier": "id2", "Error": "error2"}),
            call("Failed to insert 0 items into table2", "Error"),
            call("Failed to insert 1 items into table3", "Error"),
            call({"Source Identifier": "id3", "Error": "error3"}),
        ]
        mock_log.assert_has_calls(calls, any_order=False)

    def test_copy_data_to_dynamodb(self):
        """
        Test that copy_data_to_dynamodb returns
        False when the testing attribute is True.
        """
        print("Testing copy data to dynamodb")
        dummy_df = pd.DataFrame()
        self.db_populator.testing = True
        self.assertIsNone(
            self.db_populator.copy_data_to_dynamodb("dummy_table_name", dummy_df),
            "Failed",
        )
        self.db_populator.testing = False

    def test_get_formatted_datetime(self):
        """
        Test that get_formatted_datetime returns the current
        datetime in the correct format.
        """
        print(">>Testing get formatted datetime")
        try:
            # Call the method
            result = self.db_populator.get_formatted_datetime()
            # Check that the result is a string
            self.assertIsInstance(result, str)
            # Check that the result is in the correct format
            datetime.strptime(result, "%d-%m-%Y %H:%M:%S")
        except ValueError:
            self.fail(
                "get_formatted_datetime did not return a "
                "datetime string in the correct format."
            )
        except Exception as e:
            print(e)

    def test_split_telecom_numbers(self):
        """
        Test that split_telecom_numbers correctly splits a
        string of telecom numbers into a list of dictionaries.
        """
        print(">>Testing split telecom numbers")
        # Define a test case with a string of telecom numbers
        telecom_str = "1234567890,0987654321,1122334455"
        expected_result = [
            {"system": "phone", "value": "1234567890"},
            {"system": "phone", "value": "0987654321"},
            {"system": "phone", "value": "1122334455"},
        ]

        # Call the method with the test case
        result = self.db_populator.split_telecom_numbers(telecom_str)

        # Check that the result matches the expected result
        self.assertEqual(
            result,
            expected_result,
            "split_telecom_numbers did not return the expected result.",
        )

    def test_filter_empty_address_fields(self):
        """
        Test that filter_empty_address_fields correctly
        filters out empty fields from an address dictionary.
        """
        print(">>Testing filter empty address fields")
        # Define a test case with an address dictionary
        address = {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "",
            "zip": "12345",
            "country": " ",
            "extra": "NaN",
        }
        expected_result = {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345",
        }

        # Call the method with the test case
        result = self.db_populator.filter_empty_address_fields(address)

        # Check that the result matches the expected result
        self.assertEqual(
            result,
            expected_result,
            "filter_empty_address_fields did not return the expected result.",
        )

    def test_transpose_organisation_affiliations(self):
        """
        Test that transpose_organisation_affiliations correctly
        transposes a row of data into a schema for the
        organisation affiliations table.
        """
        print(">>Testing transpose organisation affiliations")
        # Define a test case with a row of data and a formatted datetime
        row = pd.Series(
            {
                "Identifier": 123,
                "ODSCode": "ODS123",
                "FHIRParticipatingOrganizationnIdentifier": "POI123",
                "FHIROrganizationIdentifier": "OI123",
                "Code": "Code123",
            }
        )
        formatted_datetime = "01-01-2022 00:00:00"
        expected_result = {
            "resourceType": "OrganizationAffiliation",
            "id": "123",
            "active": "true",
            "identifier": {
                "use": "secondary",
                "type": "ODS Org. Affiliation id",
                "value": "ODS123",
            },
            "participatingOrganization": "POI123",
            "organization": "OI123",
            "code": "Code123",
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
        }

        # Call the method with the test case
        result = self.db_populator.transpose_organisation_affiliations(
            formatted_datetime, row
        )

        # Check that the result matches the expected result
        self.assertEqual(
            result,
            expected_result,
            "transpose_organisation_affiliations did not "
            "return the expected result.",
        )

    def test_transpose_healthcare_services(self):
        """
        Test that transpose_healthcare_services correctly transposes a
        row of data into a schema for the healthcare services table.
        """
        print(">>Testing transpose healthcare services")
        # Define a test case with a row of data and a formatted datetime
        row = pd.Series(
            {
                "Identifier": 123,
                "OldDosUID": "ODS123",
                "OldDosID": "ODI123",
                "Name ": "Test Name",
                "Type": "Test Type",
                "LocationID": "LID123",
                "Telecom": "1234567890,0987654321,1122334455",
                "ProvidedByID": "PID123",
            }
        )
        formatted_datetime = "01-01-2022 00:00:00"
        expected_result = {
            "resourceType": "HealthcareService",
            "id": "123",
            "active": "true",
            "identifier": [
                {
                    "type": "UID",
                    "use": "oldDoS",
                    "value": "ODS123",
                },
                {
                    "type": "ID",
                    "use": "oldDoS",
                    "value": "ODI123",
                },
            ],
            "name": "Test Name",
            "type": {
                "system": "",
                "code": "",
                "display": "Test Type",
            },
            "location": "LID123",
            "telecom": [
                {"system": "phone", "value": "1234567890"},
                {"system": "phone", "value": "0987654321"},
                {"system": "phone", "value": "1122334455"},
            ],
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "providedBy": "PID123",
        }

        # Call the method with the test case
        result = self.db_populator.transpose_healthcare_services(
            formatted_datetime, row
        )

        # Check that the result matches the expected result
        self.assertEqual(
            result,
            expected_result,
            "transpose_healthcare_services did not " "return the expected result.",
        )

    def test_transpose_organisations(self):
        """
        Test that transpose_organisations correctly transposes a row
        of data into a schema for the organisations table.
        """
        print(">>Testing transpose organisations")
        # Define a test case with a row of data and a formatted datetime
        row = pd.Series(
            {
                "Identifier": 123,
                "ODSCode": "ODS123",
                "Name": "Test Name",
                "Type": "Test Type",
                "LocationID": "LID123",
                "Telecom": "1234567890,0987654321,1122334455",
                "Line1": "123 Main St",
                "Line2": "Apt 4B",
                "Line3": "",
                "City": "Anytown",
                "District": "Anydistrict",
                "PostalCode": "12345",
            }
        )
        formatted_datetime = "01-01-2022 00:00:00"
        expected_result = {
            "resourceType": "Organization",
            "id": "123",
            "active": "true",
            "identifier": {
                "use": "secondary",
                "type": "ODS",
                "value": "ODS123",
            },
            "name": "Test Name",
            "type": "Test Type",
            "location": "LID123",
            "telecom": [
                {"system": "phone", "value": "1234567890"},
                {"system": "phone", "value": "0987654321"},
                {"system": "phone", "value": "1122334455"},
            ],
            "Address": [
                {
                    "line": ["123 Main St", "Apt 4B"],
                    "city": "Anytown",
                    "district": "Anydistrict",
                    "postalCode": "12345",
                }
            ],
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
        }

        # Call the method with the test case
        result = self.db_populator.transpose_organisations(formatted_datetime, row)

        # Check that the result matches the expected result
        self.assertEqual(
            result,
            expected_result,
            "transpose_organisations did not return the expected result.",
        )

    def test_transpose_locations(self):
        """
        Test that transpose_locations correctly transposes a row
        of data into a schema for the locations table.
        """
        print(">>Testing transpose locations")
        # Define a test case with a row of data and a formatted datetime
        row = pd.Series(
            {
                "Identifier": 123,
                "Name": "Test Name",
                "Line1": "123 Main St",
                "Line2": "Apt 4B",
                "Line3": "",
                "City": "Anytown",
                "District": "Anydistrict",
                "PostalCode": "12345",
                "Latitude": 12.3456789,
                "Longitude": 98.7654321,
                "ManagingOrg": "MO123",
            }
        )
        formatted_datetime = "01-01-2022 00:00:00"
        expected_result = {
            "resourceType": "Location",
            "id": "123",
            "active": "true",
            "name": "Test Name",
            "address": [
                {
                    "line": ["123 Main St", "Apt 4B"],
                    "city": "Anytown",
                    "district": "Anydistrict",
                    "postalCode": "12345",
                }
            ],
            "position": {
                "latitude": "12.3456789",
                "longitude": "98.7654321",
            },
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "managingOrganization": "MO123",
        }

        # Call the method with the test case
        result = self.db_populator.transpose_locations(formatted_datetime, row)

        # Check that the result matches the expected result
        self.assertEqual(
            result,
            expected_result,
            "transpose_locations did not return the expected result.",
        )


if __name__ == "__main__":
    unittest.main()
