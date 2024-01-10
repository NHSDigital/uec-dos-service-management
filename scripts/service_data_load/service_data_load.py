#!/usr/bin/env python3
import pandas as pd
import uuid
import datetime
import boto3
from boto3.dynamodb.conditions import Attr


def generate_random_id():
    # Generate a random 16-digit ID
    return str(uuid.uuid4().int)[3:19]


# Function to get the current date and time in UK format
def get_formatted_datetime():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%d-%m-%Y %H:%M:%S")


# Read the Excel file
df = pd.read_excel("./Filtered_odscodes.xlsx")


# Schema mapping function
def map_to_json_schema(row):
    return {
        "id": generate_random_id(),
        "identifier": [
            {"type": "UID", "use": "oldDoS", "value": row["uid"]},
            {"type": "ID", "use": "oldDoS", "value": row["id"]},
        ],
        "type": {
            "system": "https://terminology.hl7.org/CodeSystem/service-type",
            "code": "64",
            "display": "Pharmacy",
        },
        "active": "true",
        "name": row["dosrewrite_name"],
        "odscode": row["modified_odscode"],
        "createdDateTime": get_formatted_datetime(),
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": get_formatted_datetime(),
        "providedBy": "",
        "location": "",
    }


def map_to_json_schema2(duplicate_rows, groupkey):
    id_mapping = []
    uid_mapping = []
    odscode_map = groupkey
    for index, row in duplicate_rows.iterrows():
        id_mapping.append(row["id"])
        uid_mapping.append(row["uid"])
    return {
        "id": generate_random_id(),
        "identifier": [
            {"type": "UID", "use": "oldDoS", "value": uid_mapping},
            {"type": "ID", "use": "oldDoS", "value": id_mapping},
        ],
        "type": {
            "system": "https://terminology.hl7.org/CodeSystem/service-type",
            "code": "64",
            "display": "Pharmacy",
        },
        "active": "true",
        "name": "Community Pharmacy Consultation Service",
        "odscode": odscode_map,
        "createdDateTime": get_formatted_datetime(),
        "createdBy": "Admin",
        "modifiedBy": "Admin",
        "modifiedDateTime": get_formatted_datetime(),
        "providedBy": "",
        "location": "",
    }


def write_to_dynamodb(table_name, json_data_list):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    for json_data in json_data_list:
        table.put_item(Item=json_data)


def update_services_providedby(table_name, json_data_list):
    dynamodb = boto3.resource("dynamodb")
    healthcare_table = dynamodb.Table(table_name)
    organization_table = dynamodb.Table("organisations")

    for json_data in json_data_list:
        odscode_value = json_data["odscode"]
        # Perform a scan on the Organization table
        response = organization_table.scan(
            FilterExpression=Attr("identifier.value").eq(odscode_value)
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
    location_table = dynamodb.Table("locations")

    for json_data in json_data_list:
        odscode_value = json_data["odscode"]
        # Perform a scan on the Organization table
        response = location_table.scan(
            FilterExpression=Attr("lookup_field").eq(odscode_value)
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


write_table_name = "healthcare_services"

# Create a list to store all mapped JSON data
json_data_list = []

# Iterate through each row, apply schema mapping, and append to the list
for groupkey, group in df.groupby("modified_odscode"):
    unique_rows = group[
        group["dosrewrite_name"] != "Community Pharmacy Consultation Service"
    ]
    duplicate_rows = group[
        group["dosrewrite_name"] == "Community Pharmacy Consultation Service"
    ]
    for index, row in unique_rows.iterrows():
        json_data = map_to_json_schema(row)
        json_data_list.append(json_data)

    json_data = map_to_json_schema2(duplicate_rows, groupkey)
    json_data_list.append(json_data)
    write_to_dynamodb(write_table_name, json_data_list)
    update_services_providedby(write_table_name, json_data_list)
    update_services_location(write_table_name, json_data_list)

print("All data written to all_data.json successfully!")
