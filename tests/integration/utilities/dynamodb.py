import boto3
import logging
logger = logging.getLogger("dynamo-logger")

dynamodb = boto3.resource("dynamodb")


def get_record_by_id(tablename, id: str):
    # dynamodb = get_table_resource()
    #
    # table = dynamodb.Table(tablename)
    # logger.info("table name %s", table)
    # response = table.get_item(Key={"id": id})
    # logger.info("Found key %s.", response)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('healthcare_services-dr-559')
    response = table.get_item(
    Key={
        'id': '1'
    }
    )
    print(response)
    # return response


def add_record(tablename, item):
    dynamodb = get_table_resource()
    table = dynamodb.Table(tablename)
    response = table.put_item(Item=item, TableName=tablename)
    return response


def update_record(tablename, id: str, hospital_name: str, hospital_location: str):
    dynamodb = get_table_resource()
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


def delete_record(tablename, id):
    dynamodb = get_table_resource()
    table = dynamodb.Table(tablename)
    response = table.delete_item(Key={"id": id}, TableName=table)
    return response
