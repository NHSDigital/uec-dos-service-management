import boto3
from botocore.exceptions import ClientError
from common import utilities
from aws_lambda_powertools import Tracer


TABLE_NAME = "healthcare_services"
tracer = Tracer(service="healthcare_service")


@tracer.capture_method
def get_table_resource():
    dynamodb_resource = boto3.resource("dynamodb")
    return dynamodb_resource


@tracer.capture_method
def get_record_by_id(id: str):
    dynamodb = get_table_resource()
    hs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = hs_table.get_item(Key={"id": id})
    return response


@tracer.capture_method
def add_record(item):
    dynamodb = get_table_resource()
    hs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    response = hs_table.put_item(
        Item=item, TableName=utilities.get_table_name(TABLE_NAME)
    )
    return response


@tracer.capture_method
def update_record(item):
    return add_record(item)


@tracer.capture_method
def delete_record(id):
    dynamodb = get_table_resource()
    hs_table = dynamodb.Table(utilities.get_table_name(TABLE_NAME))
    try:
        response = hs_table.delete_item(
            Key={"id": id}, TableName=utilities.get_table_name(TABLE_NAME)
        )
    except ClientError as ce:
        print(ce)
        response = {}
    return response
