import boto3
from chalicelib.common import utilities

TABLE_NAME = "healthcare_services"


def get_table_resource():
    dynamodb_resource = boto3.resource("dynamodb")
    return dynamodb_resource


def get_record_by_id(id: str):
    dynamodb = get_table_resource()
    hcs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = hcs_table.get_item(Key={"id": id})
    return response


def add_record(item):
    dynamodb = get_table_resource()
    hcs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = hcs_table.put_item(
        Item=item, TableName=utilities.get_table_name(TABLE_NAME)
    )
    return response


def update_record(id: str, hospital_location: str, hospital_name: str):
    dynamodb = get_table_resource()
    hcs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = hcs_table.update_item(
        Key={"id": id},
        UpdateExpression="SET HospitalLocation= :h_location, HospitalName = :h_name",
        ExpressionAttributeValues={
            ":h_location": hospital_location,
            ":h_name": hospital_name,
        },
        ReturnValues="UPDATED_NEW",
    )
    return response


def delete_record(id):
    dynamodb = get_table_resource()
    hcs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = hcs_table.delete_item(
        Key={"id": id}, TableName=utilities.get_table_name(TABLE_NAME)
    )
    return response
