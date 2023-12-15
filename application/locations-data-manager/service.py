import boto3
from common import utilities

TABLE_NAME = "locations"


def get_table_resource():
    dynamodb_resource = boto3.resource("dynamodb")
    return dynamodb_resource


def get_record_by_id(id: str):
    dynamodb = get_table_resource()
    l_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = l_table.get_item(Key={"id": id})
    return response


def add_record(item):
    dynamodb = get_table_resource()
    l_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = l_table.put_item(
        Item=item, TableName=utilities.get_table_name(TABLE_NAME)
    )
    return response


def update_record(id: str, hospital_name: str, hospital_location: str):
    dynamodb = get_table_resource()
    l_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
  
    item = {
        "id": id,
        "HospitalLocation": hospital_location,
        "HospitalName": hospital_name,
    }

    response = l_table.put_item(
        Item=item, TableName=utilities.get_table_name(TABLE_NAME)
    )
    return response


def delete_record(id):
    dynamodb = get_table_resource()
    l_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = l_table.delete_item(
        Key={"id": id}, TableName=utilities.get_table_name(TABLE_NAME)
    )
    return response
