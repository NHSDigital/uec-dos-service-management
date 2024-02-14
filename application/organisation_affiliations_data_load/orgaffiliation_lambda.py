#!/usr/bin/env python3
import boto3
from boto3.dynamodb.conditions import Attr

from common import common_functions

# SSM Parameter names
ssm_base_api_url = "/data/api/lambda/ods/domain"
ssm_param_id = "/data/api/lambda/client_id"
ssm_param_sec = "/data/api/lambda/client_secret"

# DynamoDB table name
dynamodb_table_name = "organisation_affiliations"


def lambda_handler(event, context):
    print("Fetching organizations data.")
    fetch_orgaffiliation()


def process_orgaffiliation(organizations):
    processed_data = []

    for resvari in organizations:
        org = resvari.get("resource")
        if org.get("resourceType") == "OrganizationAffiliation":
            processed_attributes = {
                "resourceType": org.get("resourceType"),
                "id": common_functions.generate_random_id(),
                "identifier": {
                    "use": "secondary",
                    "type": "ODS Org. Affiliation id",
                    "value": org.get("id"),
                },
                "active": "true",
                "periodStart": org.get("period", {}).get("start", ""),
                "organization": "",
                "participatingOrganization": "",
                "lookup_field_Org": org.get("organization", {})
                .get("identifier", {})
                .get("value", ""),
                "lookup_field_parti": org.get("participatingOrganization", {})
                .get("identifier", {})
                .get("value", ""),
                "code": org.get("code"),
                "createdDateTime": common_functions.get_formatted_datetime(),
                "createdBy": "Admin",
                "modifiedBy": "Admin",
                "modifiedDateTime": common_functions.get_formatted_datetime(),
            }

            processed_data.append(processed_attributes)

    return processed_data


def write_to_dynamodborgaffili(table_name, processed_data):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    for json_data in processed_data:
        table.put_item(Item=json_data)


def update_orgaffiliation_org(table_name, processed_data):
    dynamodb = boto3.resource("dynamodb")
    orgaffiliation_table = dynamodb.Table(table_name)
    organization_table = dynamodb.Table("organisations")

    for json_data in processed_data:
        odscode_value = json_data["lookup_field_Org"]
        # Perform a scan on the Organization table
        response = organization_table.scan(
            FilterExpression=Attr("identifier.value").eq(odscode_value)
        )

        # If matching records are found, update the healthcare_services table
        if response["Count"] > 0:
            organization_record = response["Items"][0]
            orgaffiliation_id = organization_record["id"]

            orgaffiliation_table.update_item(
                Key={"id": json_data["id"]},
                UpdateExpression="SET organization = :val",
                ExpressionAttributeValues={":val": orgaffiliation_id},
            )


def update_orgaffiliation_partiorg(table_name, processed_data):
    dynamodb = boto3.resource("dynamodb")
    orgaffiliation_table = dynamodb.Table(table_name)
    organization_table = dynamodb.Table("organisations")

    for json_data in processed_data:
        odscode_value = json_data["lookup_field_parti"]
        # Perform a scan on the Organization table
        response = organization_table.scan(
            FilterExpression=Attr("identifier.value").eq(odscode_value)
        )

        # If matching records are found, update the healthcare_services table
        if response["Count"] > 0:
            organization_record = response["Items"][0]
            orgaffiliation_id = organization_record["id"]

            orgaffiliation_table.update_item(
                Key={"id": json_data["id"]},
                UpdateExpression="SET participatingOrganization = :val",
                ExpressionAttributeValues={":val": orgaffiliation_id},
            )


def fetch_orgaffiliation():
    print("Getting ODS API key to fetch Org.Affiliation data.")
    api_endpoint = common_functions.get_ssm(ssm_base_api_url)
    api_endpoint += "/fhir/OrganizationAffiliation?active=true"
    headers = common_functions.get_headers(
        ssm_base_api_url, ssm_param_id, ssm_param_sec
    )
    odscode_params = common_functions.read_excel_values()

    # Get worskpace table name
    workspace_table_name = common_functions.get_table_name(dynamodb_table_name)

    for odscode_param in odscode_params:
        print("Iterating individual ODS codes")
        # Call the function to read from the ODS API and write to the output file
        response_data = common_functions.read_ods_api(
            api_endpoint, headers, odscode_param
        )

        # Process and load data to json file
        if response_data:
            organizations = response_data.get("entry", [])
            print("Processing the response and mapping to DynamoDB schema")
            processed_data = process_orgaffiliation(organizations)
            print("Writing to Org. Affiliation DynamoDB table")
            write_to_dynamodborgaffili(workspace_table_name, processed_data)
            print("Updating Organization ID")
            update_orgaffiliation_org(workspace_table_name, processed_data)
            print("Updating Participating Organization ID")
            update_orgaffiliation_partiorg(workspace_table_name, processed_data)

            print(f"Data fetched successfully for ODS code {odscode_param}")
        else:
            print(
                f"Failed to fetch data from the ODS API for ODS code {odscode_param} "
            )
