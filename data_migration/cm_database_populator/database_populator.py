#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import boto3
import pandas as pd
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from typing import Any, Dict, List


class DatabasePopulator:
    def __init__(self) -> None:
        """
        Initialize DatabasePopulator with S3 and DynamoDB clients.
        """
        print("Working in " + os.getcwd())
        try:
            with open("database_populator_config.json") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading config file: {e}")
            raise

        # Check if we are in a testing state
        self.testing = config.get("testing", False)

        if not self.testing:
            # If we are not in a testing state, initialize S3 and DynamoDB
            # clients
            self.s3 = boto3.client(config["s3"])
            self.dynamodb = boto3.resource(config["dynamodb"])
            self.ddbclient = boto3.client(config["ddbclient"])
        else:
            print("***S3 and DynamoDB disabled***")

        self.bucket_name = config["bucket_name"]
        self.file_key = config["file_key"]
        self.FHIR_entities = config["FHIR_entities"]
        self.fails = {entity["db_table_name"]: [] for entity in self.FHIR_entities}
        self.maximum_insert_fails = config["maximum_insert_fails"]
        self.insert_fails = 0
        self.log_file = config["log_file"]
        self.setup_logger()

    def setup_logger(self) -> None:
        """
        Set up the logger for the application.

        This method initializes a logger with two handlers: a file handler
        that writes log messages to a file, and a console handler that writes
        log messages to the console.
        """
        removed = self.remove_old_log_file(self.log_file)

        # Set up the logger - logging level can be changed to DEBUG for more
        # detailed output
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Log the start of the process
        if removed:
            self.log(f"Old log file {self.log_file} removed.")
        else:
            self.log(
                f"Log file {self.log_file} does not exist." f" It will be created."
            )

    def log(self, message: str, level: str = "") -> None:
        """
        Log a message at the specified level.
        """
        levels = {
            "Debug": self.logger.debug,
            "": self.logger.info,
            "Warning": self.logger.warning,
            "Error": self.logger.error,
        }
        log_message = f"{level} {message}"
        levels[level](log_message)

    def log_failures(self) -> None:
        """
        Log the failures to the console and file
        """
        for table, fails in self.fails.items():
            self.log(f"Failed to insert {len(fails)} " f"items into {table}", "Error")
            for fail in fails:
                self.log(fail)
            if self.insert_fails > self.maximum_insert_fails:
                self.log(
                    f"Failure limit({self.maximum_insert_fails}) reached."
                    " Script aborted.",
                    "Error",
                )

    def remove_old_log_file(self, log_file: str) -> bool:
        """
        Remove the old log file if it exists.

        Returns:
        True if the file was removed, False otherwise.
        """
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
        """
        Populate the database with data from an Excel file in S3.

        Returns:
        bool: True if the database was populated successfully,
        False otherwise.
        """
        self.log(
            "\n*****************************************\n"
            + "* Running the database populator script *\n"
            + "*****************************************\n"
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
                    self.copy_data_to_dynamodb(FHIR_entity["db_table_name"], df)
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

    def copy_data_to_dynamodb(self, table_name: str, df: pd.DataFrame) -> None:
        """
        Copy data from a DataFrame to a DynamoDB table.

        Args:
            table_name (str): The name of the DynamoDB table.
            df (pd.DataFrame): The DataFrame containing the data.
        """
        if table_name not in [entity["db_table_name"] for entity in self.FHIR_entities]:
            self.log(f"Table not found: {table_name}", "Error")
            return

        if not self.testing:
            table = self.dynamodb.Table(table_name)
        else:
            table = {"table_name": table_name}

        for index, row in df.iterrows():
            data_item = self.transpose_into_schema(table_name, row)
            self.insert_into_table(table, data_item)

    def get_formatted_datetime(self) -> str:
        """
        Get the current datetime formatted as a string.

        Returns:
            str: The current datetime.
        """
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime("%d-%m-%Y %H:%M:%S")

    def split_telecom_numbers(self, telecom_str: str) -> List[Dict[str, str]]:
        """
        Split a string of telecom numbers into a list of dictionaries.

        Args:
            telecom_str (str): The string of telecom numbers.

        Returns:
            List[Dict[str, str]]: The list of telecom numbers.
        """
        telecom_numbers = []
        if isinstance(telecom_str, str):
            # Split the "telecom" field by ',' to get individual telephone
            # numbers
            telecom_list = telecom_str.split(",")
            for telecom_item in telecom_list:
                telecom_item = telecom_item.strip()
                telecom_numbers.append({"system": "phone", "value": telecom_item})
        return telecom_numbers

    def filter_empty_address_fields(self, address: Dict[str, str]) -> Dict[str, str]:
        """
        Filter out empty fields from an address dictionary.

        Args:
            address (Dict[str, str]): The address dictionary.

        Returns:
            Dict[str, str]: The filtered address dictionary.
        """
        filtered_address = {}
        for k, v in address.items():
            if isinstance(v, str) and v.strip() != "" and v.strip().lower() != "nan":
                filtered_address[k] = v
        return filtered_address

    def transpose_organisation_affiliations(
        self, formatted_datetime: str, row: pd.Series
    ) -> Dict[str, Any]:
        """
        Transpose a row of data into a schema for the
        organisation affiliations table.

        Args:
            table_name (str): The name of the table.
            row (pd.Series): The row of data.

        Returns:
            Dict[str, Any]: The transposed data item.
        """
        schema = {
            "resourceType": "OrganizationAffiliation",
            "id": str(row["Identifier"]),
            "active": "true",
            "identifier": {
                "use": "secondary",
                "type": "ODS Org. Affiliation id",
                "value": str(row["ODSCode"]),
            },
            "participatingOrganization": str(
                row["FHIRParticipatingOrganizationnIdentifier"]
            ),
            "organization": row["FHIROrganizationIdentifier"],
            "code": row["Code"],
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
        }

        if row["ODSCode"] in [
            "",
            None,
            "n/a",
            "N/A",
            "nan",
            "NOT FOUND",
            "NO ID",
        ]:  # If the identifier value field is
            # blank, null, n/a, N/A, NOT FOUND or NO ID
            # Remove the identifier field from the
            schema.pop("identifier")

        return schema

    def transpose_healthcare_services(
        self, formatted_datetime: str, row: pd.Series
    ) -> Dict[str, Any]:
        """
        Transpose a row of data into a schema
        for the healthcare services table.

        Args:
            table_name (str): The name of the table.
            row (pd.Series): The row of data.

        Returns:
            Dict[str, Any]: The transposed data item.
        """
        telecom_numbers = self.split_telecom_numbers(row["Telecom"])
        schema = {
            "resourceType": "HealthcareService",
            "id": str(row["Identifier"]),
            "active": "true",
            "identifier": [
                {
                    "type": "UID",
                    "use": "oldDoS",
                    "value": row["OldDosUID"],
                },
                {
                    "type": "ID",
                    "use": "oldDoS",
                    "value": row["OldDosID"],
                },
            ],
            "name": row["Name "],
            "type": {
                "system": "",
                "code": "",
                "display": row["Type"],
            },
            "location": row["LocationID"],
            "telecom": telecom_numbers,
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "providedBy": row["ProvidedByID"],
        }
        if not telecom_numbers:
            schema.pop("telecom")
        if row["ProvidedByID"] in [
            "",
            None,
            "N/A",
            "NaN",
            "NOT FOUND",
            "NO ID",
        ]:  # If the partOf field is blank, null, n/a, N/A, or NO ID
            # Remove the partOf field from the schema
            schema.pop("providedBy")

        return schema

    def transpose_organisations(
        self, formatted_datetime: str, row: pd.Series
    ) -> Dict[str, Any]:
        """
        Transpose a row of data into a schema for the organisations table.

        Args:
            table_name (str): The name of the table.
            row (pd.Series): The row of data.

        Returns:
            Dict[str, Any]: The transposed data item.
        """
        telecom_numbers = self.split_telecom_numbers(row["Telecom"])
        streetAdress = [str(row["Line1"]), str(row["Line2"]), str(row["Line3"])]
        address = {
            "line": streetAdress,
            "city": str(row["City"]),
            "district": str(row["District"]),
            "postalCode": str(row["PostalCode"]),
        }
        filtered_address = self.filter_empty_address_fields(address)
        schema = {
            "resourceType": "Organization",
            "id": str(row["Identifier"]),
            "active": "true",
            "identifier": {
                "use": "secondary",
                "type": "ODS",
                "value": str(row["ODSCode"]),
            },
            "name": str(row["Name"]),
            "type": row["Type"],
            "location": row["LocationID"],
            "telecom": telecom_numbers,
            "Address": filtered_address,
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
        }
        if not telecom_numbers:
            schema.pop("telecom")
        if not filtered_address:
            schema.pop("Address")
        if row["ODSCode"] in [
            "",
            None,
            "n/a",
            "N/A",
            "NaN",
            "NOT FOUND",
            "NO ID",
        ]:  # If the identifier value field is
            # blank, null, n/a, N/A, NOT FOUND or NO ID
            # Remove the identifier field from the schema
            schema.pop("identifier")
        if row["LocationID"] in [
            "",
            None,
            "n/a",
            "N/A",
            "NaN",
            "NOT FOUND",
            "NO ID",
        ]:  # If the location value field is
            # blank, null, n/a, N/A, NOT FOUND or NO ID
            # Remove the location field from the schema
            schema.pop("location")

        return schema

    def transpose_locations(
        self, formatted_datetime: str, row: pd.Series
    ) -> Dict[str, Any]:
        """
        Transpose a row of data into a schema for the locations table.

        Args:
            table_name (str): The name of the table.
            row (pd.Series): The row of data.

        Returns:
            Dict[str, Any]: The transposed data item.
        """

        streetAddress = [str(row["Line1"]), str(row["Line2"]), str(row["Line3"])]

        address = {
            "line": streetAddress,
            "city": str(row["City"]),
            "district": str(row["District"]),
            "postalCode": str(row["PostalCode"]),
        }
        filtered_address = self.filter_empty_address_fields(address)
        schema = {
            "resourceType": "Location",
            "id": str(row["Identifier"]),
            "active": "true",
            "name": row["Name"],
            "address": [filtered_address],
            "position": {
                "latitude": str(
                    Decimal(row["Latitude"]).quantize(
                        Decimal("0.0000001"), rounding=ROUND_HALF_UP
                    )
                ),
                "longitude": str(
                    Decimal(row["Longitude"]).quantize(
                        Decimal("0.0000001"), rounding=ROUND_HALF_UP
                    )
                ),
            },
            "createdBy": "Admin",
            "createdDateTime": formatted_datetime,
            "modifiedBy": "Admin",
            "modifiedDateTime": formatted_datetime,
            "managingOrganization": str(row["ManagingOrg"]),
        }
        if not filtered_address:
            schema.pop("Address")
        if row["ManagingOrg"] in [
            "",
            None,
            "N/A",
            "NOT FOUND",
            "NO ID",
        ]:  # If the partOf field is
            # blank, null, n/a, N/A, or NO ID
            schema.pop(
                "managingOrganization"
            )  # Remove the partOf field from the schema
        if row["Latitude"] in [
            "",
            None,
            "N/A",
            "NOT FOUND",
            "NO ID",
        ]:  # If the Latitude field is
            # blank, null, n/a, N/A, or NO ID
            # Remove the position field from the schema
            schema.pop("position")
        elif row["Longitude"] in [
            "",
            None,
            "N/A",
            "NOT FOUND",
            "NO ID",
        ]:  # If the Longitude field is
            # blank, null, n/a, N/A, or NO ID
            # Remove the position field from the schema
            schema.pop("position")

        return schema

    def transpose_into_schema(self, table_name: str, row: pd.Series) -> Any:
        """
        Transpose a row of data into a schema for a given table.

        Args:
            table_name (str): The name of the table.
            row (pd.Series): The row of data.

        Returns:
            Dict[str, Any]: The transposed data item.
        """

        formatted_datetime = self.get_formatted_datetime()
        self.log("\nRow Data:\n" + str(row), "Debug")

        if table_name == "organisation_affiliations":
            return self.transpose_organisation_affiliations(formatted_datetime, row)
        elif table_name == "healthcare_services":
            return self.transpose_healthcare_services(formatted_datetime, row)
        elif table_name == "organisations":
            return self.transpose_organisations(formatted_datetime, row)
        elif table_name == "locations":
            return self.transpose_locations(formatted_datetime, row)
        else:
            self.log(f"Unknown table: {table_name}", "Error")

    def insert_into_table(self, table: Any, data_item: Dict[str, Any]) -> None:
        """
        Insert a data item into a DynamoDB table.

        This method takes a DynamoDB table and a data item as input,
        and attempts to insert the data item into the table.
        If the insertion fails, an error message is logged and the
        data item is added to the `fails` attribute.

        Args:
            table (Any): The DynamoDB table.
            data_item (Dict[str, Any]): The data item.
        """
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
        """
        Main execution of the script.
        """
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


if __name__ == "__main__":
    db_populator = DatabasePopulator()
    db_populator.main()
