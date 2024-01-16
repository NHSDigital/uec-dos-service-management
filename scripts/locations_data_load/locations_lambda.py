#!/usr/bin/env python3

import requests

import pandas as pd
import boto3
import uuid
import datetime
from boto3.dynamodb.conditions import Attr


def lambda_handler(event, context):
    print("Fetching organizations data.")
    fetch_organizations()
    print("Fetching Y organizations data.")
    fetch_Y_organizations()


def read_ods_api(api_endpoint, headers, params):
    token = get_api_token()
    headers = {"Authorization": "Bearer " + token}
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


def process_organizations(organizations):
    processed_data = []

    for resvars in organizations:
        org = resvars.get("resource")
        if org.get("resourceType") == "Organization":
            try:
                uprn = (
                    org.get("address")[0]
                    .get("extension")[0]
                    .get("extension")[1]
                    .get("valueString")
                )
            except TypeError:
                uprn = "NA"

            capitalized_address = [
                capitalize_address_item(address_item)
                for address_item in org.get("address", [])
                if isinstance(address_item, dict)
            ]

            processed_attributes = {
                "id": generate_random_id(),
                "lookup_field": org.get("id"),
                "active": "true",
                "name": org.get("name").title(),
                "Address": capitalized_address,
                "createdDateTime": get_formatted_datetime(),
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": get_formatted_datetime(),
                "UPRN": uprn,
                "position": {"longitude": "", "latitude": ""},
                "managingOrganization": "",
            }
            if uprn == "NA":
                processed_attributes.pop("UPRN")
            processed_data.append(processed_attributes)
    return processed_data


def write_to_dynamodb(table_name, processed_data):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    for item in processed_data:
        identifier_value = item.get("lookup_field", {})

        # Check if the identifier already exists in DynamoDB
        if not data_exists(table, identifier_value):
            # If the data doesn't exist, insert it into DynamoDB
            table.put_item(Item=item)

    # Call the function to update records in DynamoDB based on lookup_field
    update_records(dynamodb)


def data_exists(table, identifier_value):
    response = table.scan(FilterExpression=Attr("lookup_field").eq(identifier_value))
    items = response.get("Items")
    return bool(items)


dynamodb = boto3.resource("dynamodb")


def update_records(dynamodb):
    org_table = dynamodb.Table("organisations")
    locations_table = dynamodb.Table("locations")
    org_response = org_table.scan()
    locations_response = locations_table.scan()
    org_items = org_response.get("Items")
    locations_items = locations_response.get("Items")

    for locations_item in locations_items:
        locations_id = locations_item.get("id")
        if locations_item.get("managingOrganization") == "":
            locations_lookup_field_value = locations_item.get("lookup_field")

            if locations_lookup_field_value:
                for org_item in org_items:
                    org_identifier_value = org_item.get("identifier", {}).get(
                        "value", ""
                    )
                    if org_identifier_value == locations_lookup_field_value:
                        org_id = org_item.get("id")
                        locations_table.update_item(
                            Key={"id": locations_id},
                            UpdateExpression="SET managingOrganization = :val",
                            ExpressionAttributeValues={":val": org_id},
                        )


odscode_file_path = "./ODS_Codes.xlsx"


def read_excel_values(odscode_file_path):
    # Read values from the Excel file
    excel_data = pd.read_excel(odscode_file_path)
    param1_values = excel_data["ODS_Codes"].tolist()

    # # Hardcoded values for param2
    param2_value = [
        "OrganizationAffiliation:primary-organization",
        "OrganizationAffiliation:participating-organization",
    ]

    # list of dictionaries with the desired format
    params = [
        {"primary-organization": val, "_include": param2_value} for val in param1_values
    ]

    return params


token_api_endpoint = "https://beta.ods.dc4h.link//authorisation/auth/realms/terminology/protocol/openid-connect/token"


def get_api_token():
    ssm_param_id = "/data/api/lambda/client_id"
    ssm_param_sec = "/data/api/lambda/client_secret"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "Keep-alive",
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": get_ssm(ssm_param_id, ssm_param_sec)[0],
        "client_secret": get_ssm(ssm_param_id, ssm_param_sec)[1],
    }

    response = requests.post(url=token_api_endpoint, headers=headers, data=data)
    token = response.json().get("access_token")

    return token


# Get parameters from store
def get_ssm(id, secret):
    ssm = boto3.client("ssm")
    client_id = ssm.get_parameter(Name=id)["Parameter"]["Value"]
    client_secret = ssm.get_parameter(Name=secret, WithDecryption=True)["Parameter"][
        "Value"
    ]
    return client_id, client_secret


# DynamoDB table name
dynamodb_table_name = "locations"


# def write_to_json(output_file_path, processed_data):
#     import json
#     with open(output_file_path, "a") as output_file:
#         json.dump(processed_data, output_file, indent=2)
#         output_file.write("\n")


# # Iterate over Excel values and make API requests
def fetch_organizations():
    api_endpoint = "https://beta.ods.dc4h.link/fhir/OrganizationAffiliation?active=true"
    failed_to_fetch = "Failed to fetch data from the ODS API."
    odscode_params = read_excel_values(odscode_file_path)
    for odscode_param in odscode_params:
        # Call the function to read from the ODS API and write to the output file
        response_data = read_ods_api(api_endpoint, headers=None, params=odscode_param)

        # Process and load data to json file
        if response_data:
            organizations = response_data.get("entry", [])
            processed_data = process_organizations(organizations)
            write_to_dynamodb(dynamodb_table_name, processed_data)
            # output_file_path = "./location.json"
            # write_to_json(output_file_path, processed_data)

        else:
            print(failed_to_fetch)

    if response_data:
        print("Data fetched successfully.")

    else:
        print(failed_to_fetch)


# fetch Y code organizations
def fetch_Y_organizations():
    api_endpoint_Y = "https://beta.ods.dc4h.link/fhir/Organization?active=true"
    failed_to_fetch = "Failed to fetch data from the ODS API."
    params_Y = {"type": "RO209"}
    Y_response_data = read_ods_api(api_endpoint_Y, headers=None, params=params_Y)

    # Process and load data to json file
    if Y_response_data:
        organizations = Y_response_data.get("entry", [])
        processed_data = process_organizations(organizations)
        write_to_dynamodb(dynamodb_table_name, processed_data)
        # output_file_path = "./location.json"
        # write_to_json(output_file_path, processed_data)

    else:
        print(failed_to_fetch)

    if Y_response_data:
        print("Y Data fetched successfully.")

    else:
        print(failed_to_fetch)
