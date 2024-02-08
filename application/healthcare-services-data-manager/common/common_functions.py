import os
import boto3
import requests
import uuid
import datetime
import pandas as pd
from io import BytesIO


def get_table_name(table_name):
    workspace_table_name = table_name
    if os.getenv("WORKSPACE") is not None and os.getenv("WORKSPACE") != "":
        workspace_table_name = table_name + "-" + os.getenv("WORKSPACE")
    return workspace_table_name


# Get parameters from store
def get_ssm(name):
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
    return response


def get_api_token(ssm_base_api_url, ssm_param_id, ssm_param_sec):
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


def get_headers(ssm_base_api_url, ssm_param_id, ssm_param_sec):
    token = get_api_token(ssm_base_api_url, ssm_param_id, ssm_param_sec)
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


def read_excel_values():
    bucket_name = os.getenv("S3_DATA_BUCKET")
    file_key = os.getenv("ODS_CODES_XLSX_FILE")
    # Read values from the Excel file
    s3 = boto3.client("s3")
    excel_object = s3.get_object(Bucket=bucket_name, Key=file_key)
    excel_data = pd.read_excel(BytesIO(excel_object["Body"].read()))
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
