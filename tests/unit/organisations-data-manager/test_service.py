from chalicelib import service
import boto3

from moto import mock_dynamodb

mock_id = "999"
mock_hospital_name = "PyTest"
mock_hospital_location = "London"

mock_post_id = "998"
mock_post_hospital_name = "PostName"
mock_post_hospital_location = "PostTown"

mock_revised_hospital_name = "RevisedName"
mock_revised_hospital_location = "RevisedLocation"


@mock_dynamodb
def create_mock_dynamodb():
    "Create a mock implementation of the database table"
    dynamodb = boto3.resource("dynamodb")
    table_name = service.TABLE_NAME
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


def build_mock_data(id, hospital_name, hospital_location):
    "Return an item record for insert"
    data = {
        "id": id,
        "HospitalName": hospital_name,
        "HospitalLocation": hospital_location,
    }
    return data


# TODO doesn't work
@mock_dynamodb
def load_mock_data(data: map):
    "Load mock data to the table"
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(service.TABLE_NAME)
    table.put_item(Item=data, TableName=service.TABLE_NAME)


@mock_dynamodb
def test_get_record_by_id():
    "Test get_record_by_id method"
    table = create_mock_dynamodb()
    data = build_mock_data(mock_id, mock_hospital_name, mock_hospital_location)
    table.put_item(Item=data, TableName=service.TABLE_NAME)
    response = service.get_record_by_id(mock_id)
    assert response["Item"]["id"] == mock_id
    assert response["Item"]["HospitalName"] == mock_hospital_name
    assert response["Item"]["HospitalLocation"] == mock_hospital_location


@mock_dynamodb
def test_add_record():
    "Test add record method - eg used by POST"
    table = create_mock_dynamodb()
    response = table.get_item(Key={"id": mock_post_id})
    assert ("Item" in response) is False
    write_data = build_mock_data(
        mock_post_id, mock_post_hospital_name, mock_post_hospital_location
    )
    service.add_record(write_data)
    response = table.get_item(Key={"id": mock_post_id})
    assert response["Item"]["id"] == mock_post_id
    assert response["Item"]["HospitalName"] == mock_post_hospital_name
    assert response["Item"]["HospitalLocation"] == mock_post_hospital_location


@mock_dynamodb
def test_update_record():
    "Test update record method - eg used by PUT"
    table = create_mock_dynamodb()
    data = build_mock_data(mock_id, mock_hospital_name, mock_hospital_location)
    table.put_item(Item=data, TableName=service.TABLE_NAME)
    response = table.get_item(Key={"id": mock_id})
    assert response["Item"]["id"] == mock_id
    assert response["Item"]["HospitalName"] == mock_hospital_name
    assert response["Item"]["HospitalLocation"] == mock_hospital_location
    response = service.update_record(
        mock_id, mock_revised_hospital_location, mock_revised_hospital_name
    )
    assert response["Attributes"]["HospitalName"] == mock_revised_hospital_name
    assert response["Attributes"]["HospitalLocation"] == mock_revised_hospital_location


@mock_dynamodb
def test_delete_record_by_id():
    "Test delete_record method first adding and then checking it exists"
    table = create_mock_dynamodb()
    data = build_mock_data(mock_id, mock_hospital_name, mock_hospital_location)
    table.put_item(Item=data, TableName=service.TABLE_NAME)
    response = service.get_record_by_id(mock_id)
    assert response["Item"]["id"] == mock_id
    service.delete_record(mock_id)
    response = table.get_item(Key={"id": mock_id})
    assert ("Item" in response) is False
