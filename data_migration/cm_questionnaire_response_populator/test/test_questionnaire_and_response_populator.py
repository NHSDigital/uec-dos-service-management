import unittest
import tempfile
import pandas as pd
from datetime import datetime
from questionnaire_and_response_populator import QuestionnairePopulator
from unittest.mock import patch, call, MagicMock


class TestQuestionnairePopulator(unittest.TestCase):
    @patch("boto3.client")
    @patch("boto3.resource")
    @patch("os.environ.get")
    def setUp(self, mock_get, mock_resource, mock_client):
        print(">>Setting up")
        # Set maxDiff to None to display the full diff for assertion errors
        self.maxDiff = None
        try:
            mock_get.return_value = "False"
            self.db_populator = QuestionnairePopulator()
            if not self._testMethodName.startswith("test_logging"):
                self.patcher = patch.object(self.db_populator, "setup_logger")
                self.mock_setup_logger = self.patcher.start()
        except Exception as e:
            print(e)

        self.obj = QuestionnairePopulator()

        # Mocking the dependencies of the method
        self.obj.get_formatted_datetime = MagicMock(return_value="2024-09-17 12:00:00")
        self.obj.log = MagicMock()
        self.obj.transpose_questionnaires = MagicMock()
        self.obj.transpose_questionnaire_responses = MagicMock()
        self.obj.transpose_questionnaire_collection_sheet = MagicMock()
        self.obj.populate_database = MagicMock()
        self.obj.log_failures = MagicMock()

        # Mocking instance attributes
        self.obj.fails = {"mock_table": []}

        # Attributes
        self.obj.testing = False
        self.obj.insert_fails = 0

        # Mock the `table` object
        self.table = MagicMock()
        self.table.table_name = "mock_table"

        # Mocking the questions dictionary
        self.obj.questions = {"1": "question1", "2": "question2"}

    def tearDown(self):
        if hasattr(self, "patcher"):
            self.patcher.stop()

    def test_init(self):
        print(">>Testing init")
        try:
            self.assertEqual(self.db_populator.testing, False)
        except Exception as e:
            print(e)

    def test_logging_file_path(self):
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
    def test_remove_old_log_file(self, mock_exists):
        print(">>Testing remove old log file")
        # Mock os.path.exists to always return False
        mock_exists.return_value = False
        result = self.db_populator.remove_old_log_file("non_existent_file.log")
        self.assertFalse(
            result,
        )

    @patch("logging.FileHandler")
    def test_logging_setup_logger(self, mock_file_handler):
        print(">>Testing setup logger")
        with patch("logging.getLogger"):
            self.db_populator.setup_logger()
            try:
                mock_file_handler.assert_called_once_with(self.db_populator.log_file)
            except AssertionError:
                print("FileHandler was not called with the correct " "log file path.")

    def test_logging_log(self):
        print(">>Testing log")
        with patch.object(self.db_populator.logger, "info") as mock_info:
            self.db_populator.log("Test message")
            try:
                mock_info.assert_called_once_with(" " + "Test message")
            except AssertionError:
                print(
                    "Logger's info method was not called with the correct " "message."
                )

    @patch.object(QuestionnairePopulator, "log")
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
            self.db_populator.copy_data_to_dynamodb(
                "dummy_table_name", "sheet_name", dummy_df
            ),
            "Failed",
        )
        self.db_populator.testing = False

    def test_get_formatted_datetime(self):
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

    def test_transpose_questionnaire_collection_sheet(self):
        row = pd.Series(
            {"Link ID": 1, "Question Text": "question1", "other_data": "something"}
        )
        expected_result = {"1": "question1"}

        self.db_populator.transpose_questionnaire_collection_sheet(row)
        result = self.db_populator.questions
        self.assertEqual(result, expected_result)

    def test_transpose_questionnaire_responses(self):
        question = {"1": "question1", "2": "question2"}

        row = pd.Series(
            {
                1: 35,
                2: 75.4,
                "responseIdentifier": "ABABABABABABABA",
                "QuestionnaireURL": "https://abababa.aba",
                "status": "mock status",
                "healthcareServiceId": "1234567890987654321",
                "healthcareServiceName": "mock HS name",
                "authoredDate": "2024-07-24T12:00:00+00:18",
                "questionairreIdentifier": "bbbbbbbbbbbbbb",
            }
        )
        formatted_datetime = "01-01-2022 00:00:00"
        expected_result = {
            "resourceType": "QuestionnaireResponse",
            "id": "ABABABABABABABA",
            "questionnaire": "https://abababa.aba",
            "status": "mock status",
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "subject": {
                "reference": "HealthcareService/1234567890987654321",
                "display": "mock HS name",
            },
            "authored": "2024-07-24T12:00:00+00:18",
            "identifier": {"use": "secondary", "type": "ID", "value": "bbbbbbbbbbbbbb"},
            "item": [
                {"linkId": "1", "text": "question1", "answer": [{"valueInteger": 35}]},
                {
                    "linkId": "2",
                    "text": "question2",
                    "answer": [{"valueDecimal": "75.4"}],
                },
            ],
        }

        # Call the method with the test case
        result = self.db_populator.transpose_questionnaire_responses(
            formatted_datetime, row, question
        )

        # Check that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_transpose_questionnaires(self):
        row = pd.Series(
            {
                1: "mock text 1",
                "type": "mock type 1",
                2: "mock text 2",
                "type.1": "mock type 2",
                "Id": "1234567890987654321",
                "identifier": "ababababababa",
                "title": "mock title",
                "name": "mock name",
                "version": 1,
                "lastReviewDate": "2024-07-24 00:00:00",
                "subjectType": "mock subject type",
                "effectivePeriod.start": "2024-07-24 00:00:00",
                "effectivePeriod.end": "2030-07-24 00:00:00",
                "useContext.code.system": "https://mock.system",
                "useContext.code.code": "mock use code",
                "useContext.valueCodeableConcept.text": "ServiceTypeA",
            }
        )

        formatted_datetime = "01-01-2022 00:00:00"
        expected_result = {
            "resourceType": "Questionnaire",
            "id": "1234567890987654321",
            "identifier": {"use": "secondary", "type": "ID", "value": "ababababababa"},
            "url": "https://example.org/fhir/Questionnaire/capacity-management-questionnaire-001",
            "status": "active",
            "title": "mock title",
            "name": "mock name",
            "version": 1,
            "lastReviewDate": "2024-07-24 00:00:00",
            "subjectType": "mock subject type",
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "effectivePeriod": {
                "start": "2024-07-24 00:00:00",
                "end": "2030-07-24 00:00:00",
            },
            "useContext": [
                {
                    "code": {
                        "system": "https://mock.system",
                        "code": "mock use code",
                    },
                    "valueCodeableConcept": {"text": "ServiceTypeA"},
                }
            ],
            "item": [
                {"linkId": "1", "text": "mock text 1", "type": "mock type 1"},
                {"linkId": "2", "text": "mock text 2", "type": "mock type 2"},
            ],
        }

        # Call the method with the test case
        result = self.db_populator.transpose_questionnaires(formatted_datetime, row)

        # Check that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_main_successful_population(self):
        """Test successful database population without any failures."""
        self.obj.populate_database.return_value = False  # No abortion
        self.obj.fails = {}  # No partial failures
        self.obj.insert_fails = 0  # No insertion failures

        # Call the main method
        self.obj.main()

        # Assertions
        self.obj.populate_database.assert_called_once()
        self.obj.log.assert_any_call(
            "\n**********************************\n"
            + "* Database population successful *\n"
            + "**********************************\n"
        )
        self.obj.log_failures.assert_not_called()

    def test_main_partial_insertions(self):
        """Test when there are partial insertions (some data failed to insert)."""
        self.obj.populate_database.return_value = False  # No abortion
        self.obj.fails = {"mock_table": [{"id": "123", "Error": "Insert failed"}]}
        self.obj.insert_fails = 1  # Simulate a failure count

        # Call the main method
        self.obj.main()

        # Assertions
        self.obj.populate_database.assert_called_once()
        self.obj.log.assert_any_call("Partial insertions for mock_table")
        self.obj.log.assert_any_call("  {'id': '123', 'Error': 'Insert failed'}")
        self.obj.log_failures.assert_called_once()

    def test_main_critical_failure(self):
        """Test when the process is aborted due to critical failure."""
        self.obj.populate_database.return_value = True  # Abortion occurred
        self.obj.fails = {"mock_table": []}  # No partial insertions
        self.obj.insert_fails = 0  # No insertion failures

        # Call the main method
        self.obj.main()

        # Assertions
        self.obj.populate_database.assert_called_once()
        self.obj.log.assert_called_once_with(
            "Critical failure. Process aborted", "Error"
        )
        self.obj.log_failures.assert_not_called()

    def test_main_insert_failures_without_critical_abort(self):
        """Test when there are insert failures but no critical abortion."""
        self.obj.populate_database.return_value = False
        self.obj.fails = {"mock_table": []}
        self.obj.insert_fails = 5

        # Call the main method
        self.obj.main()

        # Assertions
        self.obj.populate_database.assert_called_once()
        self.obj.log_failures.assert_called_once()

    def test_insert_data_successfully(self):
        """Test inserting data when not in testing mode."""
        self.obj.testing = False
        data_item = {"id": "123", "name": "test_item"}

        # Call the method
        self.obj.insert_into_table(self.table, data_item)

        # Assertions to verify correct behavior
        self.obj.log.assert_any_call("Inserting data into table: mock_table")
        self.table.put_item.assert_called_once_with(Item=data_item)
        self.obj.log.assert_any_call(f"Dyno Data:{data_item}\nInserted.")
        self.assertEqual(self.obj.insert_fails, 0)
        self.assertEqual(len(self.obj.fails["mock_table"]), 0)

    def test_insert_data_in_testing_mode(self):
        """Test inserting data in testing mode (no data should be inserted)."""
        self.obj.testing = True  # Testing mode
        data_item = {"id": "123", "name": "test_item"}

        # Call the method
        self.obj.insert_into_table(self.table, data_item)

        # Assertions to verify correct behavior
        self.obj.log.assert_any_call(
            f"dyno Data:{data_item}\nTesting mode: data not inserted."
        )
        self.table.put_item.assert_not_called()  # put_item should not be called in testing mode
        self.assertEqual(self.obj.insert_fails, 0)
        self.assertEqual(len(self.obj.fails["mock_table"]), 0)

    def test_insert_data_with_exception(self):
        """Test exception handling when insert fails."""
        self.obj.testing = False  # Not in testing mode
        data_item = {"id": "123", "name": "test_item"}

        # Simulate an exception when calling put_item
        self.table.put_item.side_effect = Exception("Insert error")

        # Call the method
        self.obj.insert_into_table(self.table, data_item)

        # Assertions to verify correct behavior
        self.obj.log.assert_any_call(
            "Error inserting data into table: Insert error", "Error"
        )
        self.assertEqual(self.obj.insert_fails, 1)
        self.assertEqual(
            self.obj.fails["mock_table"],
            [{"Source Identifier": "123", "Error": "Insert error"}],
        )

    def test_transpose_into_schema_questionnaires(self):
        row = pd.Series({"id": 1, "name": "Test"})
        self.obj.transpose_into_schema("questionnaires", "some_sheet", row)

        # Check if get_formatted_datetime was called
        self.obj.get_formatted_datetime.assert_called_once()
        # Check if transpose_questionnaires was called with the right arguments
        self.obj.transpose_questionnaires.assert_called_once_with(
            "2024-09-17 12:00:00", row
        )
        # Verify the log method was called to log the row data
        self.obj.log.assert_called_with("\nRow Data:\n" + str(row), "Debug")

    def test_transpose_into_schema_responses(self):
        row = pd.Series({"id": 1, "name": "Response"})
        self.obj.transpose_into_schema("questionnaire_responses", "some_sheet", row)

        # Check if get_formatted_datetime was called
        self.obj.get_formatted_datetime.assert_called_once()
        # Check if transpose_questionnaire_responses was called with the right arguments
        self.obj.transpose_questionnaire_responses.assert_called_once_with(
            "2024-09-17 12:00:00", row, self.obj.questions
        )
        # Verify the log method was called to log the row data
        self.obj.log.assert_called_with("\nRow Data:\n" + str(row), "Debug")

    def test_transpose_into_schema_collection_sheet(self):
        row = pd.Series({"id": 1, "name": "Sheet Test"})
        self.obj.transpose_into_schema("some_table", "Questionnaire-001-010", row)

        # Check if get_formatted_datetime was called
        self.obj.get_formatted_datetime.assert_called_once()
        # Check if transpose_questionnaire_collection_sheet was called with the right arguments
        self.obj.transpose_questionnaire_collection_sheet.assert_called_once_with(row)
        # Verify the log method was called to log the row data
        self.obj.log.assert_called_with("\nRow Data:\n" + str(row), "Debug")

    def test_unknown_table(self):
        row = pd.Series({"id": 1, "name": "Unknown"})
        self.obj.transpose_into_schema("unknown_table", "some_sheet", row)

        # Check if get_formatted_datetime was called
        self.obj.get_formatted_datetime.assert_called_once()
        # Check if the log method was called to log the error for unknown table
        self.obj.log.assert_called_with("Unknown table: unknown_table", "Error")
