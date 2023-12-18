import json
import boto3
import logging

logger = logging.getLogger("dynamo-logger")

dynamodb = boto3.resource("dynamodb")


def get_record_by_id(tablename, id: str):
    table = dynamodb.Table(tablename)
    response = table.get_item(Key={"id": id})
    logger.info("Found key %s.", id)
    return response


def add_record(tablename, item):
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=item, TableName=tablename)
    return response


def add_record_from_file(tablename, file_name):
    with open("data_json/location_post_body.json") as json_file:
        json_data = json.load(json_file)
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=json_data, TableName=tablename)
    return response


def update_record(tablename, id: str, hospital_name: str, hospital_location: str):
    table = dynamodb.Table(tablename)
    response = table.update_item(
        Key={"id": id},
        UpdateExpression="SET HospitalLocation= :h_location, HospitalName = :h_name",
        ExpressionAttributeValues={
            ":h_location": hospital_location,
            ":h_name": hospital_name,
        },
        ReturnValues="UPDATED_NEW",
    )
    return response


def delete_record_by_id(tablename, id):
    table = dynamodb.Table(tablename)
    response = table.delete_item(Key={"id": id})
    logger.info("Deleted key %s.", id)
    return response
