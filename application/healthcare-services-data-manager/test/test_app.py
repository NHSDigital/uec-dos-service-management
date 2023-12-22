import app
import service
import boto3
import json
from moto import mock_dynamodb

mock_id = "2690664379947884"
mock_active = "true"
mock_created_by = "Admin"
mock_timestamp_created = "15-12-2023 16:00:12"
mock_timestamp_modified = "15-12-2023 16:00:12"
mock_lookup_field = "QYG"
mock_modified_by = "Admin"
mock_name = "Nhs Somewhere And Nowhere Integrated Care Board"


@mock_dynamodb
def create_mock_dynamodb():
    "Create a mock implementation of the dynamodb healthcare_services table"
    dynamodb = boto3.resource("dynamodb")
    table_name = service.TABLE_NAME
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


def build_mock_healthcare_services_item():
    "Return a test item record for insert"
    data = {
        "id": mock_id,
        "active": mock_active,
        "createdBy": mock_created_by,
        "createdDateTime": mock_timestamp_created,
        "lookup_field": mock_lookup_field,
        "modifiedBy": mock_modified_by,
        "modifiedDateTime": mock_timestamp_modified,
        "name": mock_name,
    }
    return data


@mock_dynamodb
def test_get_record_by_id():
    table = create_mock_dynamodb()
    healthcare_services_record = build_mock_healthcare_services_item()
    table.put_item(Item=healthcare_services_record, TableName=service.TABLE_NAME)
    "Test GET method"
    mock_context = None
    mock_load = load_sample_event_from_file("mock_proxy_get_event.json")
    response = app.lambda_handler(mock_load, mock_context)
    assert str(response["statusCode"]) == "HTTPStatus.OK"
    response_body = json.loads(response["body"])
    assert response_body["Item"]["name"] == mock_name


@mock_dynamodb
def test_put_record():
    table = create_mock_dynamodb()
    "Test PUT method"
    mock_context = None
    mock_load = load_sample_event_from_file("mock_proxy_put_event.json")
    response = app.lambda_handler(mock_load, mock_context)
    assert str(response["statusCode"]) == "HTTPStatus.OK"
    healthcare_services_record = table.get_item(Key={"id": mock_id})
    assert healthcare_services_record["Item"]["name"] == "Nhs PUT Integrated Care Board"


@mock_dynamodb
def test_post_record():
    table = create_mock_dynamodb()
    "Test POST method"
    mock_context = None
    mock_load = load_sample_event_from_file("mock_proxy_post_event.json")
    response = app.lambda_handler(mock_load, mock_context)
    assert str(response["statusCode"]) == "HTTPStatus.OK"
    healthcare_services_record = table.get_item(Key={"id": mock_id})
    assert (
        healthcare_services_record["Item"]["name"] == "Nhs POST Integrated Care Board"
    )


@mock_dynamodb
def test_delete_record_by_id():
    table = create_mock_dynamodb()
    healthcare_services_record = build_mock_healthcare_services_item()
    table.put_item(Item=healthcare_services_record, TableName=service.TABLE_NAME)
    "Test DELETE method"
    mock_context = None
    mock_load = load_sample_event_from_file("mock_proxy_delete_event.json")
    app.lambda_handler(mock_load, mock_context)
    healthcare_services_record = table.get_item(Key={"id": mock_id})
    assert "Item" not in healthcare_services_record


def load_sample_event_from_file(filename) -> dict:
    """
    Loads and validate test events from the file system
    """
    event_file_name = (
        "./application/healthcare-services-data-manager/test/events/" + filename
    )
    with open(event_file_name) as file_handle:
        json_str = file_handle.read()
        event = json.loads(json_str)
        return event
