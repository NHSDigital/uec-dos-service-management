#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import boto3
from io import BytesIO
import datetime

# Initialize the S3 and DynamoDB clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
ddbclient = boto3.client("dynamodb")

# Specify the S3 bucket name and Excel file key
bucket_name = "nhse-uec-cm-dev-databucket"
file_key = "CapacityManagementFullDataset.xlsx"

# A list of the relevant dynamoDB tables, and the names of the corresponding
# tabs in the spreadsheet. These must be manually confirmed to be correct
# or the script won't work

FHIR_entities = [
    {"db_table_name": "organisations", "spreadsheet_tab_name": "FHIR Organization"},
    {
        "db_table_name": "healthcare_services",
        "spreadsheet_tab_name": "FHIR Healthcare Service",
    },
    {
        "db_table_name": "organisation_affiliations",
        "spreadsheet_tab_name": "FHIR Organization affiliation",
    },
    {"db_table_name": "locations", "spreadsheet_tab_name": "FHIR Location"},
]


def populate_database():
    print("****************************************************************")
    print("**********Running the database populator script*****************")
    print("****************************************************************")

    for FHIR_entity in FHIR_entities:
        # Perform a check to determine if the dynamoDB table is empty or not
        print(FHIR_entity)
        print(
            ":::::Running populator script for table: " + FHIR_entity["db_table_name"]
        )
        # Use the S3 `get_object` method to read the Excel file directly into a DataFrame
        excel_object = s3.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_excel(
            BytesIO(excel_object["Body"].read()),
            sheet_name=FHIR_entity["spreadsheet_tab_name"],
        )
        # Copy the data from the spreadsheet into the relevant table
        copy_data_to_dynamodb(FHIR_entity["db_table_name"], df)


def copy_data_to_dynamodb(table_name, df):
    table = dynamodb.Table(table_name)

    for index, row in df.iterrows():
        data_item = transpose_into_schema(table_name, row)
        insert_into_table(table, data_item)


# Define a function to get the current date and time in UK format
def get_formatted_datetime():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%d-%m-%Y %H:%M:%S")


def split_telecom_numbers(telecom_str):
    telecom_numbers = []
    if isinstance(telecom_str, str):
        # Split the "telecom" field by ',' to get individual telephone numbers
        telecom_list = telecom_str.split(",")
        for telecom_item in telecom_list:
            telecom_item = telecom_item.strip()  # Remove leading/trailing spaces
            telecom_numbers.append({"system": "phone", "value": telecom_item})
    return telecom_numbers


def filter_empty_address_fields(address):
    filtered_address = {}
    for k, v in address.items():
        if isinstance(v, str) and v.strip() != "" and v.strip().lower() != "nan":
            filtered_address[k] = v
    return filtered_address


def transpose_into_schema(table_name, row):
    formatted_datetime = get_formatted_datetime()
    print("Row Data:", row)

    if table_name == "organisation_affiliations":
        return transpose_organisation_affiliations(row, formatted_datetime)
    elif table_name == "healthcare_services":
        return transpose_healthcare_services(row, formatted_datetime)
    elif table_name == "organisations":
        return transpose_organisations(row, formatted_datetime)
    elif table_name == "locations":
        return transpose_locations(row, formatted_datetime)
    else:
        raise ValueError("Unsupported table name: {}".format(table_name))


def transpose_organisation_affiliations(row, formatted_datetime):
    schema = {
        "resourceType": "OrganizationAffiliation",
        "id": str(row["Identifier"]),
        "active": "true",
        "identifier": [
            {
                "value": str(row["Identifier"]),
            }
        ],
        "participatingOrganization": str(
            row["FHIRParticipatingOrganizationnIdentifier"]
        ),
        "organization": row["FHIROrganizationIdentifier"],
        "healthcareService": row["FHIRHealthcareServiceIdentifier"],
        "location": row["FHIRLocationIdentifier"],
        "createdBy": "Admin",
        "createdDateTime": formatted_datetime,
        "modifiedBy": "Admin",
        "modifiedDateTime": formatted_datetime,
    }

    # Create a list of the keys in the schema
    schema_keys = list(schema.keys())

    # Remove empty keys from the schema
    for key in schema_keys:
        if (
            schema[key] is None
            or schema[key] == ""
            or schema[key] == "NO ID"
            or schema[key] == "NOT FOUND"
        ):
            schema.pop(key)

    return schema


def transpose_healthcare_services(row, formatted_datetime):
    telecom_numbers = split_telecom_numbers(row["Telecom"])
    schema = {
        "resourceType": "HealthcareService",
        "id": str(row["Identifier"]),
        "identifier": [
            {
                "use": "official",
                "value": str(row["Identifier"]),
            }
        ],
        "active": "True",
        "name": row["Name "],
        "type": row["Type"],
        "location": row["LocationID"],
        "createdBy": "Admin",
        "createdDateTime": formatted_datetime,
        "modifiedBy": "Admin",
        "modifiedDateTime": formatted_datetime,
        "providedBy": row["ProvidedByID"],
    }

    # Add the telecom field to the schema if it has a value
    if telecom_numbers:
        schema["telecom"] = telecom_numbers

    # Remove empty keys from the schema
    for key in schema.keys():
        if (
            schema[key] is None
            or schema[key] == ""
            or schema[key] == "N/A"
            or schema[key] == "NO ID"
        ):
            schema.pop(key)

    return schema


def transpose_organisations(row, formatted_datetime):
    telecom_numbers = split_telecom_numbers(row["Telecom"])
    address = {
        "line1": str(row["Line1"]),
        "line2": str(row["Line2"]),
        "line3": str(row["Line3"]),
        "city": str(row["City"]),
        "district": str(row["Discrict"]),
        "postalcode": str(row["PostalCode"]),
    }
    filtered_address = filter_empty_address_fields(address)
    schema = {
        "resourceType": "Organization",
        "id": str(row["Identifier"]),
        "identifier": [
            {
                "use": "official",
                "value": str(row["Identifier"]),
            }
        ],
        "active": "true",
        "type": row["Type"],
        "name": str(row["Name"]),
        "createdDateTime": formatted_datetime,
        "partOf": str(row["partof"]),
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": formatted_datetime,
    }

    # Add the telecom field to the schema if it has a value
    if telecom_numbers:
        schema["telecom"] = telecom_numbers

    if filtered_address:
        schema["Address"] = filtered_address

    # Remove empty keys from the schema
    schema_copy = schema.copy()
    schema_keys = list(schema_copy.keys())
    for key in schema_keys:
        if (
            schema_copy[key] is None
            or schema_copy[key] == ""
            or schema_copy[key] == "N/A"
            or schema_copy[key] == "NO ID"
            or schema_copy[key] == "0"
        ):
            schema_copy.pop(key)

    return schema_copy


def transpose_locations(row, formatted_datetime):
    address = {
        "line1": str(row["Line1"]),
        "line2": str(row["Line2"]),
        "line3": str(row["Line3"]),
        "city": str(row["City"]),
        "district": str(row["District"]),
        "postalcode": str(row["PostalCode"]),
    }
    filtered_address = filter_empty_address_fields(address)
    schema = {
        "resourceType": "Location",
        "id": str(row["Identifier"]),
        "identifier": [
            {
                "use": "official",
                "value": str(row["Identifier"]),
            }
        ],
        "status": "Active",
        "name": row["Name"],
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

    if filtered_address:
        schema["Address"] = filtered_address

    # Remove empty keys from the schema
    schema_copy = schema.copy()
    schema_keys = list(schema_copy.keys())
    for key in schema_keys:
        if (
            schema_copy[key] is None
            or schema_copy[key] == ""
            or schema_copy[key] == "N/A"
            or schema_copy[key] == "NO ID"
            or schema_copy[key] == "0"
        ):
            schema_copy.pop(key)

    return schema_copy


def insert_into_table(table, data_item):
    print("dyno Data:", data_item)
    table.put_item(Item=data_item)


if __name__ == "__main__":
    populate_database()
