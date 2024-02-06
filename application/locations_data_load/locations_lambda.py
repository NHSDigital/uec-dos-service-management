#!/usr/bin/env python3
import boto3
import uuid
import datetime
from boto3.dynamodb.conditions import Attr

from common import common_functions


# SSM Parameter names
ssm_base_api_url = "/data/api/lambda/ods/domain"
ssm_param_id = "/data/api/lambda/client_id"
ssm_param_sec = "/data/api/lambda/client_secret"


# DynamoDB table name
locations_table_name = "locations"
organisations_table_name = "organisations"

# Get worskpace table name
workspace_locations_table_name = common_functions.get_table_name(locations_table_name)


def lambda_handler(event, context):
    print("Fetching organizations data.")
    fetch_organizations()
    print("Fetching Y organizations data.")
    fetch_y_organizations()


def process_organizations(organizations):
    processed_data = []
    random_id = str(uuid.uuid4().int)[0:16]
    current_datetime = datetime.datetime.now()
    now_time = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
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
            except Exception:
                uprn = "NA"

            capitalized_address = [
                common_functions.capitalize_address_item(address_item)
                for address_item in org.get("address", [])
                if isinstance(address_item, dict)
            ]

            processed_attributes = {
                "id": random_id,
                "lookup_field": org.get("id"),
                "active": "true",
                "name": org.get("name").title(),
                "Address": capitalized_address,
                "createdDateTime": now_time,
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": now_time,
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
        if data_exists(table, identifier_value) is False:
            # If the data doesn't exist, insert it into DynamoDB
            table.put_item(Item=item)

    # Call the function to update records in DynamoDB based on lookup_field
    update_records()


def data_exists(table, identifier_value):
    response = table.scan(FilterExpression=Attr("lookup_field").eq(identifier_value))
    if response.get("Items") == []:
        return False
    else:
        return True


def update_records():
    dynamodb = boto3.resource("dynamodb")
    org_table = dynamodb.Table(workspace_locations_table_name)
    locations_table = dynamodb.Table(organisations_table_name)
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


# def write_to_json(output_file_path, processed_data):
#     import json
#     with open(output_file_path, "a") as output_file:
#         json.dump(processed_data, output_file, indent=2)
#         output_file.write("\n")


# # Iterate over Excel values and make API requests
def fetch_organizations():
    api_endpoint = common_functions.get_ssm(ssm_base_api_url)
    api_endpoint += "/fhir/OrganizationAffiliation?active=true"
    headers = common_functions.get_headers(
        ssm_base_api_url, ssm_param_id, ssm_param_sec
    )
    odscode_params = common_functions.read_excel_values()
    for odscode_param in odscode_params:
        # Call the function to read from the ODS API and write to the output file
        response_data = common_functions.read_ods_api(
            api_endpoint, headers, odscode_param
        )

        # Process and load data
        if response_data:
            organizations = response_data.get("entry", [])
            processed_data = process_organizations(organizations)
            write_to_dynamodb(workspace_locations_table_name, processed_data)
            # output_file_path = "./location.json"
            # write_to_json(output_file_path, processed_data)
            print("Data fetched successfully.")
        else:
            print("Failed to fetch data from the ODS API.")


# fetch Y code organizations
def fetch_y_organizations():
    api_endpoint_y = common_functions.get_ssm(ssm_base_api_url)
    api_endpoint_y += "/fhir/Organization?active=true"
    params_y = {"type": "RO209"}
    headers = common_functions.get_headers(
        ssm_base_api_url, ssm_param_id, ssm_param_sec
    )
    y_response_data = common_functions.read_ods_api(
        api_endpoint_y, headers, params=params_y
    )

    # Process and load data
    if y_response_data:
        organizations = y_response_data.get("entry", [])
        processed_data = process_organizations(organizations)
        write_to_dynamodb(workspace_locations_table_name, processed_data)
        # output_file_path = "./location.json"
        # write_to_json(output_file_path, processed_data)
        print("Y Data fetched successfully.")
    else:
        print("Failed to fetch data from the ODS API.")
