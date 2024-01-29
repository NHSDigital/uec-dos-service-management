#!/usr/bin/env python3

import requests
import pandas as pd
import boto3
import uuid
import datetime
from boto3.dynamodb.conditions import Attr

# SSM parameter names
ssm_base_api_url = "/data/api/lambda/ods/domain"
ssm_param_id = "/data/api/lambda/client_id"
ssm_param_sec = "/data/api/lambda/client_secret"

# ODS code excel file path
odscode_file_path = "./ODS_Codes.xlsx"


def lambda_handler(event, context):
    print("Fetching organizations data.")
    fetch_organizations()


# Get parameters from store
def get_ssm(name):
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
    return response


def get_api_token():
    api_endpoint = get_ssm(ssm_base_api_url)
    api_endpoint += (
        "//authorisation/auth/realms/terminology/protocol/openid-connect/token"
    )
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "Keep-alive",
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": get_ssm(ssm_param_id),
        "client_secret": get_ssm(ssm_param_sec),
    }

    response = requests.post(url=api_endpoint, headers=headers, data=data)
    token = response.json().get("access_token")

    return token


def get_headers():
    token = get_api_token()
    headers = {"Authorization": "Bearer " + token}
    return headers


def read_ods_api(api_endpoint, headers, params):
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


def process_organization(organizations):
    ph_org = None

    for organization in organizations:
        org = organization.get("resource")
        if (
            org.get("resourceType") == "Organization"
            and org["type"][0]["coding"][0]["display"] == "PHARMACY HEADQUARTER"
        ):
            ph_org = org
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
        processed_attributes = None

        if (
            org.get("resourceType") == "Organization"
            and org["type"][0]["coding"][0]["display"] == "PHARMACY"
        ):
            ph_org = process_organization(organizations)
            processed_attributes = process_pharmacy(org, ph_org)
        elif (
            org.get("resourceType") == "Organization"
            and org["type"][0]["coding"][0]["display"] != "PHARMACY"
        ):
            processed_attributes = process_non_pharmacy(org)
        if processed_attributes is not None:
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
        if data_exists(table, identifier_value) is False:
            # If the data doesn't exist, insert it into DynamoDB
            table.put_item(Item=item)

    # Call the function to update records in DynamoDB based on lookup_field
    update_records(table)


def data_exists(table, identifier_value):
    response = table.scan(
        FilterExpression=Attr("identifier.value").eq(identifier_value)
    )
    if response.get("Items") == []:
        return False
    else:
        return True


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
                table.update_item(
                    Key={"id": id_value},
                    UpdateExpression="SET partOf = :val",
                    ExpressionAttributeValues={":val": relevant_id},
                )

                # Print the update status
                print("Record with id " + lookup_field_value + "updated.")
            else:
                print(f"No match found for identifier value: {lookup_field_value}")
        else:
            print(
                f"Identifier value is blank for lookup_field value: {lookup_field_value}. Skipping update."
            )
    else:
        print("Lookup field value is blank. Skipping update.")


def read_excel_values(file_path):
    # Read values from the Excel file
    excel_data = pd.read_excel(file_path)

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


def fetch_organizations():
    api_endpoint = get_ssm(ssm_base_api_url)
    api_endpoint += "/fhir/OrganizationAffiliation?active=true"
    # Read values from Excel
    odscode_params = read_excel_values(odscode_file_path)

    # Get headers
    headers = get_headers()

    # DynamoDB table name
    dynamodb_table_name = "organisations"

    # Iterate over Excel values and make API requests
    for odscode_param in odscode_params:
        # Call the function to read from the ODS API and write to the output file
        response_data = read_ods_api(api_endpoint, headers, odscode_param)

        # Process and load data to json file
        if response_data:
            organizations = response_data.get("entry", [])
            processed_data = process_organizations(organizations)
            write_to_dynamodb(dynamodb_table_name, processed_data)
            print("Data fetched successfully for ODS code " + odscode_param)
        else:
            print("Failed to fetch data from the ODS API for ODS code " + odscode_param)
