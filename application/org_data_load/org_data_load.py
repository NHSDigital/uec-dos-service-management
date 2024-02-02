#!/usr/bin/env python3
import boto3
from boto3.dynamodb.conditions import Attr

from common import common_functions


# SSM parameter names
ssm_base_api_url = "/data/api/lambda/ods/domain"
ssm_param_id = "/data/api/lambda/client_id"
ssm_param_sec = "/data/api/lambda/client_secret"

# DynamoDB table name
dynamodb_table_name = "organisations"


def lambda_handler(event, context):
    print("Fetching organizations data.")
    fetch_organizations()


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
        common_functions.capitalize_address_item(address_item)
        for address_item in org.get("address", [])
        if isinstance(address_item, dict)
    ]

    processed_attributes = {
        "resourceType": org.get("resourceType"),
        "id": common_functions.generate_random_id(),
        "identifier": {"use": "secondary", "type": "ODS", "value": org.get("id")},
        "active": "true",
        "type": process_type(org.get("type", "")),
        "name": org.get("name").title(),
        "Address": capitalized_address,
        "createdDateTime": common_functions.get_formatted_datetime(),
        "partOf": "",
        "lookup_field": ph_org["id"] if ph_org else None,
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": common_functions.get_formatted_datetime(),
    }

    return processed_attributes


def process_non_pharmacy(org):
    capitalized_address = [
        common_functions.capitalize_address_item(address_item)
        for address_item in org.get("address", [])
        if isinstance(address_item, dict)
    ]

    processed_attributes = {
        "resourceType": org.get("resourceType"),
        "id": common_functions.generate_random_id(),
        "identifier": {"use": "secondary", "type": "ODS", "value": org.get("id")},
        "active": "true",
        "type": process_type(org.get("type", "")),
        "name": org.get("name").title(),
        "Address": capitalized_address,
        "createdDateTime": common_functions.get_formatted_datetime(),
        # "partOf": "",
        # "lookup_field": None,
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": common_functions.get_formatted_datetime(),
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
                print("Record with id " + lookup_field_value + " updated.")
            else:
                print(f"No match found for identifier value: {lookup_field_value}")
        else:
            print(
                f"Identifier value is blank for lookup_field value: {lookup_field_value}. Skipping update."
            )
    else:
        print("Lookup field value is blank. Skipping update.")


def fetch_organizations():
    api_endpoint = common_functions.get_ssm(ssm_base_api_url)
    api_endpoint += "/fhir/OrganizationAffiliation?active=true"
    # Read values from Excel
    odscode_params = common_functions.read_excel_values()

    # Get headers
    headers = common_functions.get_headers(
        ssm_base_api_url, ssm_param_id, ssm_param_sec
    )

    # Get worskpace table name
    workspace_table_name = common_functions.get_table_name(dynamodb_table_name)

    # Iterate over Excel values and make API requests
    for odscode_param in odscode_params:
        # Call the function to read from the ODS API and write to the output file
        response_data = common_functions.read_ods_api(
            api_endpoint, headers, odscode_param
        )

        # Process and load data to json file
        if response_data:
            organizations = response_data.get("entry", [])
            processed_data = process_organizations(organizations)
            write_to_dynamodb(workspace_table_name, processed_data)
            print("Data fetched successfully for ODS code")
            print(odscode_param)
        else:
            print("Failed to fetch data from the ODS API for ODS code")
            print(odscode_param)
