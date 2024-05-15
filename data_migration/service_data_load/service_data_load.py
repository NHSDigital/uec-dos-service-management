#!/usr/bin/env python3
import pandas as pd
import boto3
import os

from common import common_functions

# # for Aurora db connection
# import psycopg2


# handler
def lambda_handler(event, context):
    print("Running Healthcare service schema")
    schema_mapping()


# # Get parameter
# def get_ssm(name):
#     ssm = boto3.client("ssm")
#     response = ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
#     if response:
#         print ("======= fetched " + name + " from SSM successfully =========")
#     return response


# # Retrieve AWS secret
# def get_secret(secret_name):
#     secrets_extension_endpoint = "http://localhost:2773" + \
#     "/secretsmanager/get?secretId=" + \
#     secret_name

#     headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}
#     r = requests.get(secrets_extension_endpoint, headers=headers)
#
#     #load the Secrets Manager response into a Python dictionary, access the secret
#     secret = json.loads(r.text)["SecretString"]
#     print ("===== retrieved secret =======")

#     return secret[13:28]


# # Connect to Aurora DB
# def read_aurora_db():
#     aurora_endpoint = "/data/api/lambda/aurora_read_endpoint"
#     aurora_user = "/data/api/lambda/aurora_user"
#     db_name = "/data/api/lambda/aurora_db"
#     db_pass = "dev/aurora-dos-postgress-password"
#     host = get_ssm(aurora_endpoint)
#     username = get_ssm(aurora_user)
#     database = get_ssm(db_name)
#     password = get_secret(db_pass)
#     print ("==== Trying connection to aurora =======")
#     db_conn = psycopg2.connect(host=host, database=database, user=username, password=password)
#     print ("===== Connected to aurora. Querying data =====")
#     sql = "SELECT * FROM pathwaysdos.healthcareservicesrewrite limit 2;"
#     data_df = pd.io.sql.read_sql(sql, db_conn)
#     return(data_df)
#     db_conn.close()


# S3 file
file = "Filtered_odscodes.xlsx"


# Read the Excel file
def read_s3_file():
    bucket_name = os.getenv("S3_DATA_BUCKET")
    # Read values from the Excel file
    s3 = boto3.resource("s3")
    s3.Object(bucket_name, file).download_file("/tmp/" + file)

    df = pd.read_excel("/tmp/" + file)
    data = df.groupby(["modified_odscode"])
    return data


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
    day_list = []
    day_list.append(
        {
            "dayofweek": "",
            "starttime": "",
            "endtime": "",
        }
    )

    json_data_list = []
    read_file = read_s3_file()

    for groupkey, group in read_file:
        unique_rows = group[
            group["dosrewrite_name"] != "Community Pharmacy Consultation Service"
        ]

        duplicate_rows = group[
            group["dosrewrite_name"] == "Community Pharmacy Consultation Service"
        ]

        for index, row in unique_rows.iterrows():
            id_val = row["id"]
            uid_val = row["uid"]

            json_data = common_schema(
                uid_val, id_val, row["dosrewrite_name"], row["odscode"], day_list
            )
            json_data_list.append(json_data)

        id_mapping = []
        uid_mapping = []
        odscode_map = groupkey
        for index, row in duplicate_rows.iterrows():
            id_mapping.append(row["id"])
            uid_mapping.append(row["uid"])

            json_data = common_schema(
                uid_mapping,
                id_mapping,
                "Community Pharmacy Consultation Service",
                odscode_map,
                day_list,
            )
            json_data_list.append(json_data)

    write_to_dynamodb(healthcare_workspaced_table_name, json_data_list)
    update_services_providedby(healthcare_workspaced_table_name, json_data_list)
    update_services_location(healthcare_workspaced_table_name, json_data_list)

    print("All data written to Healthcareservice Table successfully!")
