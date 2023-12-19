#!/usr/bin/env python3

import requests

# import json
import pandas as pd

# from decimal import Decimal
import boto3

# from io import BytesIO
import uuid
import datetime
from boto3.dynamodb.conditions import Attr

# from boto3.dynamodb.conditions import Key

# from botocore.exceptions import ClientError


def read_ods_api(api_endpoint, headers=None, params=None):
    try:
        response = requests.get(api_endpoint, headers=headers, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            response_data = response.json()

            return response_data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def generate_random_id():
    # Generate a random 16-digit ID
    return str(uuid.uuid4().int)[0:16]


# function to get the current date and time in UK format
def get_formatted_datetime():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%d-%m-%Y %H:%M:%S")


def capitalize_line(line):
    return line.title()


def capitalize_address_item(address_item):
    capitalized_item = {}

    for key, value in address_item.items():
        if key == "line" and isinstance(value, list):
            capitalized_item[key] = [capitalize_line(line) for line in value]
        elif key in ["city", "district", "country"]:
            capitalized_item[key] = value.title()
        elif key == "postalCode":
            capitalized_item[key] = value
        elif key != "extension":
            capitalized_item[key] = value

    return capitalized_item


def process_organization(org, organizations):
    ph_org = None

    for organization in organizations:
        org1 = organization.get("resource")
        if (
            org1.get("resourceType") == "Organization"
            and org1["type"][0]["coding"][0]["display"] == "PHARMACY HEADQUARTER"
        ):
            ph_org = org1
            break

    return ph_org


def process_pharmacy(org, ph_org):
    capitalized_address = [
        capitalize_address_item(address_item)
        for address_item in org.get("address", [])
        if isinstance(address_item, dict)
    ]

    processed_attributes = {
        "resourceType": org.get("resourceType"),
        "id": generate_random_id(),
        "identifier": {"use": "secondary", "type": "ODS", "value": org.get("id")},
        "active": "true",
        "type": process_type(org.get("type", "")),
        "name": org.get("name").title(),
        "Address": capitalized_address,
        "createdDateTime": get_formatted_datetime(),
        "partOf": "",
        "lookup_field": ph_org["id"] if ph_org else None,
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": get_formatted_datetime(),
    }

    return processed_attributes


def process_non_pharmacy(org):
    capitalized_address = [
        capitalize_address_item(address_item)
        for address_item in org.get("address", [])
        if isinstance(address_item, dict)
    ]

    processed_attributes = {
        "resourceType": org.get("resourceType"),
        "id": generate_random_id(),
        "identifier": {"use": "secondary", "type": "ODS", "value": org.get("id")},
        "active": "true",
        "type": process_type(org.get("type", "")),
        "name": org.get("name").title(),
        "Address": capitalized_address,
        "createdDateTime": get_formatted_datetime(),
        # "partOf": "",
        # "lookup_field": None,
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": get_formatted_datetime(),
    }

    return processed_attributes


def process_organizations(organizations):
    processed_data = []

    for resvar in organizations:
        org = resvar.get("resource")

        if (
            org.get("resourceType") == "Organization"
            and org["type"][0]["coding"][0]["display"] == "PHARMACY"
        ):
            ph_org = process_organization(org, organizations)
            processed_attributes = process_pharmacy(org, ph_org)
        elif (
            org.get("resourceType") == "Organization"
            and org["type"][0]["coding"][0]["display"] != "PHARMACY"
        ):
            processed_attributes = process_non_pharmacy(org)

        processed_data.append(processed_attributes)

    return processed_data


def process_type(types):
    for t in types:
        if "coding" in t and isinstance(t["coding"], list):
            for coding in t["coding"]:
                if (
                    "system" in coding
                    and coding["system"] == "https://ods-prototype/role"
                ):
                    return coding.get("display", "Default_Value").title()
    return None


def write_to_dynamodb(table_name, processed_data):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    for item in processed_data:
        identifier_value = item.get("identifier", {}).get("value", "")

        # Check if the identifier already exists in DynamoDB
        if not data_exists(table, identifier_value):
            # If the data doesn't exist, insert it into DynamoDB
            table.put_item(Item=item)

    # Call the function to update records in DynamoDB based on lookup_field
    update_records(table)


def data_exists(table, identifier_value):
    response = table.scan(
        FilterExpression=Attr("identifier.value").eq(identifier_value)
    )
    items = response.get("Items")
    return bool(items)


def update_records(table):
    response = table.scan()
    items = response.get("Items")

    for item in items:
        lookup_field_value = item.get("lookup_field")
        id_value = item.get("id")

        # Check if identifier_value is not blank
        if lookup_field_value:
            identifier_response = table.scan(
                FilterExpression=Attr("identifier.value").eq(lookup_field_value)
            )

            identifier_items = identifier_response.get("Items")

            # Check if there is a match in the DynamoDB table
            if identifier_items:
                # Take the relevant id key value from the first match
                relevant_id = identifier_items[0].get("id", "")

                # Update the partOf field for the record with lookup_field_value
                update_response = table.update_item(
                    Key={"id": id_value},
                    UpdateExpression="SET partOf = :val",
                    ExpressionAttributeValues={":val": relevant_id},
                )

                # Print the update status
                print(
                    f"Record with id {lookup_field_value} updated. Status: {update_response}"
                )
            else:
                print(f"No match found for identifier value: {lookup_field_value}")
        else:
            print(
                f"Identifier value is blank for lookup_field value: {lookup_field_value}. Skipping update."
            )
    else:
        print("Lookup field value is blank. Skipping update.")


def read_excel_values(odscode_file_path):
    # Read values from the Excel file
    excel_data = pd.read_excel(odscode_file_path)

    param1_values = excel_data["ODS_Codes"].tolist()

    # Hardcoded values for param2
    param2_value = [
        "OrganizationAffiliation:primary-organization",
        "OrganizationAffiliation:participating-organization",
    ]

    # list of dictionaries with the desired format
    params = [
        {"primary-organization": val, "_include": param2_value} for val in param1_values
    ]

    return params


api_endpoint = "https://beta.ods.dc4h.link/fhir/OrganizationAffiliation?active=true"
token = ""
headers = {"Authorization": "Bearer " + token}


# ODS code excel file path
odscode_file_path = "./ODS_Codes.xlsx"

# Read values from Excel
odscode_params = read_excel_values(odscode_file_path)

# DynamoDB table name
dynamodb_table_name = "organisations"

# Iterate over Excel values and make API requests
for odscode_param in odscode_params:
    # Call the function to read from the ODS API and write to the output file
    response_data = read_ods_api(api_endpoint, headers=headers, params=odscode_param)

    # Process and load data to json file
    if response_data:
        organizations = response_data.get("entry", [])
        processed_data = process_organizations(organizations)
        write_to_dynamodb(dynamodb_table_name, processed_data)

    else:
        print("Failed to fetch data from the ODS API.")

if response_data:
    print("Data fetched successfully.")

else:
    print("Failed to fetch data from the ODS API.")
