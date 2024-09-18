#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import boto3
import tempfile
import pandas as pd
from io import BytesIO
from typing import Any, Dict
from common.common_functions import get_table_name


class QuestionnairePopulator:
    def __init__(self) -> None:
        # Get the environment variable as a string,
        # default to 'True' if it doesn't exist
        testing_str = os.environ.get("ISOLATED_TESTING", "True")

        # Convert the string to a boolean
        self.testing = testing_str.lower() in ["false", "0"]

        print("Working in " + os.getcwd())
        try:
            with open("questionnaire_and_response_populator_config.json") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            raise

        if self.testing:
            print("***S3 and DynamoDB disabled***")
        else:
            # If we are not in a testing state, initialize S3 and DynamoDB
            # clients
            self.s3 = boto3.client(config["s3"])
            self.dynamodb = boto3.resource(config["dynamodb"])
            self.ddbclient = boto3.client(config["ddbclient"])

        self.bucket_name = config["bucket_name"]
        self.file_key = config["file_key"]
        self.FHIR_entities = config["FHIR_entities"]
        self.fails = {entity["db_table_name"]: [] for entity in self.FHIR_entities}
        self.maximum_insert_fails = config["maximum_insert_fails"]
        # self.comb_sheet = config["questionnaire_combined_spreadsheet"]
        self.insert_fails = 0
        # Initialise the log file
        self.log_file = os.path.join(tempfile.gettempdir(), config["log_file"])
        self.setup_logger()

    def setup_logger(self) -> None:
        # Set up the logger - logging level can be changed to DEBUG for more
        # detailed output
        self.logger = logging.getLogger(__name__)
        # Get the log level from the environment variable,
        # default to 'DEBUG' if it doesn't exist
        log_level_name = os.environ.get("LOG_LEVEL", "DEBUG")

        # Convert the log level name to a log level number
        log_level = logging.getLevelName(log_level_name)

        if not isinstance(log_level, int):
            log_level = logging.DEBUG

        # Set the log level
        logging.basicConfig(level=log_level)

    def log(self, message: str, level: str = "") -> None:
        log_message = f"{level} {message}"
        if not hasattr(self, "logger") or not isinstance(self.logger, logging.Logger):
            print(log_message)
        else:
            levels = {
                "Debug": self.logger.debug,
                "": self.logger.info,
                "Warning": self.logger.warning,
                "Error": self.logger.error,
            }
            levels[level](log_message)

    def log_failures(self) -> None:
        for table, fails in self.fails.items():
            self.log(
                f"Failed to insert {len(fails)} " f"items into {table}",
                "Error",
            )
            for fail in fails:
                self.log(fail)
            if self.insert_fails > self.maximum_insert_fails:
                self.log(
                    f"Failure limit({self.maximum_insert_fails}) reached."
                    " Script aborted.",
                    "Error",
                )

    def remove_old_log_file(self, log_file: str) -> bool:
        removed = False
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
                removed = True
        except PermissionError:
            self.log(f"Permission denied: {log_file}", "Error")
        except Exception as e:
            self.log(f"An error occurred: {e}", "Error")
        return removed

    def populate_database(self) -> bool:
        self.log(
            "\n************************************************************\n"
            + "* Running the quuestionnaire and response populator script *\n"
            + "************************************************************\n"
        )

        self.log("Working in " + os.getcwd())
        self.log("Workbook path is " + self.file_key + "\n")
        aborted = False

        try:
            if self.testing:
                self.log("Testing mode: using local file", "Warning")
                # Create a dictionary to mimic the S3 get_object response
                with open(self.file_key, "rb") as f:
                    file_content = f.read()
                excel_object = {"Body": BytesIO(file_content)}
            else:
                # Use the S3 `get_object` method to read the Excel file
                response = self.s3.get_object(
                    Bucket=self.bucket_name, Key=self.file_key
                )
                # Read the streaming body into a BytesIO object
                excel_object = {"Body": BytesIO(response["Body"].read())}
        except FileNotFoundError:
            self.log(f"File not found: {self.file_key}", "Error")
            raise
        except Exception as e:
            self.log(f"An error occurred: {e}", "Error")
            raise

        for FHIR_entity in self.FHIR_entities:
            # Perform a check to determine if the dynamoDB table is empty or
            # not
            self.log(FHIR_entity)
            self.log(
                "Running populator script for table: " + FHIR_entity["db_table_name"]
            )
            try:
                excel_object["Body"].seek(0)
                df = pd.read_excel(
                    BytesIO(excel_object["Body"].read()),
                    sheet_name=FHIR_entity["spreadsheet_tab_name"],
                    engine="openpyxl",
                ).fillna("")

                # Copy the data from the spreadsheet into the relevant table
                if df.empty:
                    self.log("Empty sheet: " + FHIR_entity["spreadsheet_tab_name"])
                else:
                    self.copy_data_to_dynamodb(
                        FHIR_entity["db_table_name"],
                        FHIR_entity["spreadsheet_tab_name"],
                        df,
                    )
            except Exception as e:
                self.log(
                    f"Error reading data from Excel file: {e}." " Exiting script.",
                    "Error",
                )
                aborted = True
                break

            if self.insert_fails > self.maximum_insert_fails:
                self.log("Too many insert failures. Exiting script.", "Error")
                aborted = True
                break
        return aborted

    def copy_data_to_dynamodb(
        self, table_name: str, sheet_name: str, df: pd.DataFrame
    ) -> None:
        ws_table_name = get_table_name(table_name)
        if table_name not in [entity["db_table_name"] for entity in self.FHIR_entities]:
            self.log(f"Table not found: {table_name}", "Error")
            return

        if not self.testing:
            table = self.dynamodb.Table(ws_table_name)
        else:
            table = {"table_name": table_name}

        for (
            index,
            row,
        ) in df.iterrows():
            data_item = self.transpose_into_schema(ws_table_name, sheet_name, row)
            if sheet_name != "Questionnaire-001-010":
                self.insert_into_table(table, data_item)

    def get_formatted_datetime(self) -> str:
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime("%d-%m-%Y %H:%M:%S")

    questions = {}

    def transpose_questionnaire_collection_sheet(
        self, row: pd.Series
    ) -> Dict[str, Any]:
        """ """
        linkid = str(row["Link ID"])
        question = str(row["Question Text"])
        self.questions[f"{linkid}"] = question

    def transpose_questionnaire_responses(
        self, formatted_datetime: str, row: pd.Series, questions
    ) -> Dict[str, Any]:
        items = []
        nr = 1
        while True:
            if nr in row:
                if row[nr] != "":
                    try:
                        number = float(row[nr])
                        value = (
                            "valueInteger" if number.is_integer() else "valueDecimal"
                        )
                        number = (
                            int(number)
                            if value == "valueInteger"
                            else str(round(number, 1))
                        )
                    except ValueError:
                        nr += 1
                        continue

                    question = questions.get(str(nr))

                    items.append(
                        {
                            "linkId": str(nr),
                            "text": str(question),
                            "answer": [{value: number}],
                        }
                    )
            else:
                break
            nr += 1

        healthcareServiceId = row["healthcareServiceId"]
        schema = {
            "resourceType": "QuestionnaireResponse",
            "id": str(row["responseIdentifier"]),
            "questionnaire": str(row["QuestionnaireURL"]),
            "status": row["status"],
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "subject": {
                "reference": str(f"HealthcareService/{healthcareServiceId}"),
                "display": row["healthcareServiceName"],
            },
            "authored": row["authoredDate"],
            "identifier": {
                "use": "secondary",
                "type": "ID",
                "value": str(row["questionairreIdentifier"]),
            },
            "item": items,
        }

        return schema

    def transpose_questionnaires(
        self, formatted_datetime: str, row: pd.Series
    ) -> Dict[str, Any]:
        items = [{"linkId": "1", "text": row[1], "type": row["type"]}]
        nr = 2

        while True:
            if nr in row:
                if row[nr] != "":
                    items.append(
                        {
                            "linkId": str(nr),
                            "text": row[nr],
                            "type": row[f"type.{nr-1}"],
                        }
                    )
            else:
                break
            nr = nr + 1

        schema = {
            "resourceType": "Questionnaire",
            "id": str(row["Id"]),
            "identifier": {
                "use": "secondary",
                "type": "ID",
                "value": str(row["identifier"]),
            },
            "url": "https://example.org/fhir/Questionnaire/capacity-management-questionnaire-001",
            "status": "active",
            "title": row["title"],
            "name": row["name"],
            "version": row["version"],
            "lastReviewDate": str(row["lastReviewDate"]),
            "subjectType": row["subjectType"],
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "effectivePeriod": {
                "start": str(row["effectivePeriod.start"]),
                "end": str(row["effectivePeriod.end"]),
            },
            "useContext": [
                {
                    "code": {
                        "system": row["useContext.code.system"],
                        "code": row["useContext.code.code"],
                    },
                    "valueCodeableConcept": {
                        "text": row["useContext.valueCodeableConcept.text"]
                    },
                }
            ],
            "item": items,
        }
        return schema

    def transpose_into_schema(
        self, table_name: str, sheet_name: str, row: pd.Series
    ) -> Any:
        formatted_datetime = self.get_formatted_datetime()
        self.log("\nRow Data:\n" + str(row), "Debug")

        if (
            table_name == "questionnaires-" + str(os.getenv("WORKSPACE"))
            or table_name == "questionnaires"
        ):
            return self.transpose_questionnaires(formatted_datetime, row)

        elif sheet_name == "Questionnaire-001-010":
            self.transpose_questionnaire_collection_sheet(row)

        elif (
            table_name == "questionnaire_responses-" + str(os.getenv("WORKSPACE"))
            or table_name == "questionnaire_responses"
        ):
            return self.transpose_questionnaire_responses(
                formatted_datetime, row, self.questions
            )

        else:
            self.log(f"Unknown table: {table_name}", "Error")

    def insert_into_table(self, table: Any, data_item: Dict[str, Any]) -> None:
        try:
            if not self.testing:
                self.log(f"Inserting data into table: {table.table_name}")
                table.put_item(Item=data_item)
                self.log(f"Dyno Data:{data_item}\nInserted.")
            else:
                self.log(f"dyno Data:{data_item}\nTesting mode:" " data not inserted.")
        except Exception as e:
            self.log(f"Error inserting data into table: {e}", "Error")
            self.fails[table.table_name].append(
                {"Source Identifier": data_item["id"], "Error": str(e)}
            )
            self.insert_fails += 1

    def main(self) -> None:
        aborted = self.populate_database()

        for table in self.fails:
            if self.fails[table]:
                self.log("Partial insertions for " + table)
                for partial in self.fails[table]:
                    self.log(f"  {partial}")
        if aborted:
            self.log("Critical failure. Process aborted", "Error")
        elif self.insert_fails > 0:
            self.log_failures()
        else:
            self.log(
                "\n**********************************\n"
                + "* Database population successful *\n"
                + "**********************************\n"
            )


def lambda_handler(
    event, context, updateQuestionnaires=False, updateResponses=False
):  # pragma: no cover
    questionnairePopulator = QuestionnairePopulator()
    questionnairePopulator.main()


if __name__ == "__main__":  # pragma: no cover
    questionnairePopulator = QuestionnairePopulator()
    questionnairePopulator.main()
