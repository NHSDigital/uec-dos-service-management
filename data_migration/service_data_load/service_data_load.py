#!/usr/bin/env python3
import pandas as pd
import boto3
import os

from common import common_functions


def lambda_handler(event, context):
    print("Running Healthcare service schema")
    schema_mapping()


# S3 file
file = "Filtered_odscodes.xlsx"


# Read the Excel file
def read_s3_file():
    bucket_name = os.getenv("S3_DATA_BUCKET")
    # Read values from the Excel file
    s3 = boto3.client("s3")
    excel_object = s3.get_object(Bucket=bucket_name, Key=file)
    df = pd.read_excel(excel_object)
    return df


# Common schema mapping
def common_schema(value1, value2, name_value, odscode, day_list):
    time = common_functions.get_formatted_datetime()
    return {
        "id": common_functions.generate_random_id(),
        "identifier": [
            {"type": "UID", "use": "oldDoS", "value": value1},
            {"type": "ID", "use": "oldDoS", "value": value2},
        ],
        "type": {
            "system": "https://terminology.hl7.org/CodeSystem/service-type",
            "code": "64",
            "display": "Pharmacy",
        },
        "active": "true",
        "name": name_value,
        "odscode": odscode,
        "createdDateTime": time,
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": time,
        "providedBy": "",
        "location": "",
        "ServiceAvailability": day_list,
    }


def write_to_dynamodb(table_name, json_data_list):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    for json_data in json_data_list:
        table.put_item(Item=json_data)


# Get workspaced table name
locations_table_name = "locations"
organisations_table_name = "organisations"
locations_workspaced_table_name = common_functions.get_table_name(locations_table_name)
organisations_workspaced_table_name = common_functions.get_table_name(
    locations_table_name
)


def update_services_providedby(table_name, json_data_list):
    dynamodb = boto3.resource("dynamodb")
    healthcare_table = dynamodb.Table(table_name)
    organization_table = dynamodb.Table(organisations_workspaced_table_name)

    for json_data in json_data_list:
        odscode_value = json_data["odscode"]
        odscode_id = json_data["id"]

        response = organization_table.query(
            KeyConditionExpression="id = :idvalue",
            FilterExpression="identifier.#val = :val",
            ExpressionAttributeNames={"#val": "value"},
            ExpressionAttributeValues={":val": odscode_value, ":idvalue": odscode_id},
        )
        # If matching records are found, update the healthcare_services table
        if response["Count"] > 0:
            organization_record = response["Items"][0]
            org_id = organization_record["id"]

            healthcare_table.update_item(
                Key={"id": json_data["id"]},
                UpdateExpression="SET providedBy = :val",
                ExpressionAttributeValues={":val": org_id},
            )


def update_services_location(table_name, json_data_list):
    dynamodb = boto3.resource("dynamodb")
    healthcare_table = dynamodb.Table(table_name)
    location_table = dynamodb.Table(locations_workspaced_table_name)

    for json_data in json_data_list:
        odscode_value = json_data["odscode"]
        odscode_id = json_data["id"]

        response = location_table.query(
            KeyConditionExpression="id = :idvalue",
            FilterExpression="lookup_field = :val",
            ExpressionAttributeValues={":val": odscode_value, ":idvalue": odscode_id},
        )
        # If matching records are found, update the healthcare_services table
        if response["Count"] > 0:
            location_record = response["Items"][0]
            location_id = location_record["id"]

            healthcare_table.update_item(
                Key={"id": json_data["id"]},
                UpdateExpression="SET #location = :val",
                ExpressionAttributeNames={"#location": "location"},
                ExpressionAttributeValues={":val": location_id},
            )


# Iterate through each row, apply schema mapping, and append to the list
def schema_mapping():
    healthcare_table_name = "healthcare_services"
    healthcare_workspaced_table_name = common_functions.get_table_name(
        healthcare_table_name
    )
    json_data_list = []
    read_file = read_s3_file.groupby("id", "uid")

    for groupkey, group in read_file:
        unique_rows = group[
            group["dosrewrite_name"] != "Community Pharmacy Consultation Service"
        ]

        for index, row in unique_rows.iterrows():
            id_val = row["id"]
            uid_val = row["uid"]
            day_list = []
            for _, r in group.iterrows():
                if r["id"] == id_val and r["uid"] == uid_val:
                    day_list.append(
                        {
                            "dayofweek": r["dayofweek"],
                            "starttime": r["starttime"],
                            "endtime": r["endtime"],
                        }
                    )
                    break

            json_data = common_schema(
                id_val, uid_val, row["dosrewrite_name"], row["code"], day_list
            )
            json_data_list.append(json_data)

    # Move the following lines outside the loop to write data to DynamoDB after processing all groups
    write_to_dynamodb(healthcare_workspaced_table_name, json_data_list)
    update_services_providedby(healthcare_workspaced_table_name, json_data_list)
    update_services_location(healthcare_workspaced_table_name, json_data_list)

    print("All data written to Healthcareservice Table successfully!")
