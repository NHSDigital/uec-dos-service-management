import app
import service
import boto3
import json
from moto import mock_dynamodb
from types import SimpleNamespace

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
    "Create a mock implementation of the dynamodb questionnaire_responses table"
    dynamodb = boto3.resource("dynamodb")
    table_name = service.TABLE_NAME
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


def build_mock_questionnaire_responses_item():
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
    questionnaire_responses_record = build_mock_questionnaire_responses_item()
    table.put_item(Item=questionnaire_responses_record, TableName=service.TABLE_NAME)
    "Test GET method"
    lambda_context_data = load_lambda_context_from_file("lambda_context.json")
    mock_context = SimpleNamespace(**lambda_context_data)
    mock_load = load_sample_event_from_file("mock_proxy_get_event.json")
    response = app.lambda_handler(mock_load, mock_context)
    assert str(response["statusCode"]) == "200"
    response_body = json.loads(response["body"])
    assert response_body["Item"]["name"] == mock_name


@mock_dynamodb
def test_put_record():
    table = create_mock_dynamodb()
    "Test PUT method"
    lambda_context_data = load_lambda_context_from_file("lambda_context.json")
    mock_context = SimpleNamespace(**lambda_context_data)
    mock_load = load_sample_event_from_file("mock_proxy_put_event.json")
    response = app.lambda_handler(mock_load, mock_context)
    assert str(response["statusCode"]) == "200"
    questionnaire_responses_record = table.get_item(Key={"id": mock_id})
    assert (
        questionnaire_responses_record["Item"]["name"]
        == "Nhs PUT Integrated Care Board"
    )


@mock_dynamodb
def test_post_record():
    table = create_mock_dynamodb()
    "Test POST method"
    lambda_context_data = load_lambda_context_from_file("lambda_context.json")
    mock_context = SimpleNamespace(**lambda_context_data)
    mock_load = load_sample_event_from_file("mock_proxy_post_event.json")
    response = app.lambda_handler(mock_load, mock_context)
    assert str(response["statusCode"]) == "200"
    questionnaire_responses_record = table.get_item(Key={"id": mock_id})
    assert (
        questionnaire_responses_record["Item"]["name"]
        == "Nhs POST Integrated Care Board"
    )


@mock_dynamodb
def test_delete_record_by_id():
    table = create_mock_dynamodb()
    questionnaire_responses_record = build_mock_questionnaire_responses_item()
    table.put_item(Item=questionnaire_responses_record, TableName=service.TABLE_NAME)
    "Test DELETE method"
    lambda_context_data = load_lambda_context_from_file("lambda_context.json")
    mock_context = SimpleNamespace(**lambda_context_data)
    mock_load = load_sample_event_from_file("mock_proxy_delete_event.json")
    app.lambda_handler(mock_load, mock_context)
    questionnaire_responses_record = table.get_item(Key={"id": mock_id})
    assert "Item" not in questionnaire_responses_record


def load_sample_event_from_file(filename) -> dict:
    """
    Loads and validate test events from the file system
    """
    event_file_name = (
        "./application/questionnaire-responses-data-manager/test/events/" + filename
    )
    with open(event_file_name) as file_handle:
        json_str = file_handle.read()
        event = json.loads(json_str)
        return event


def load_lambda_context_from_file(filename):
    """
    load Lambda context from a JSON file
    """
    context_file_name = "tests/integration/lambda_context_json/" + filename
    with open(context_file_name, "r") as f:
        return json.load(f)
