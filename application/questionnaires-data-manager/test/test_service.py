import service
import boto3

from moto import mock_dynamodb

mock_id = "999"
mock_active = "true"
mock_postcode = "EX2 5SE"
mock_city = "Exeter"
mock_country = "England"
mock_line_1 = "Hexagon House"
mock_line_2 = "Pynes Hill"
mock_created_by = "Admin"
mock_timestamp_created = "15-12-2023 16:00:12"
mock_timestamp_modified = "15-12-2023 16:00:12"
mock_lookup_field = "QYG"
mock_modified_by = "Admin"
mock_managing_organisation = ""
mock_name = "Nhs Somewhere And Nowhere Integrated Care Board"
mock_lat = "50.708140"
mock_long = "-3.488450"


mock_post_id = "998"
mock_updated_name = "Updated name"
mock_status_update = "false"


@mock_dynamodb
def create_mock_dynamodb():
    "Create a mock implementation of the dynamodb questionnaires table"
    dynamodb = boto3.resource("dynamodb")
    table_name = service.TABLE_NAME
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


def build_mock_questionnaires_item():
    "Return an item record for insert"
    data = {
        "id": mock_id,
        "active": mock_active,
        "Address": [
            {
                "city": mock_city,
                "country": mock_country,
                "line": [mock_line_1, mock_line_2],
                "postalCode": mock_postcode,
            }
        ],
        "createdBy": mock_created_by,
        "createdDateTime": mock_timestamp_created,
        "lookup_field": mock_lookup_field,
        "managingOrganization": mock_managing_organisation,
        "modifiedBy": mock_modified_by,
        "modifiedDateTime": mock_timestamp_modified,
        "name": mock_name,
        "position": {"latitude": mock_lat, "longitude": mock_long},
    }
    return data


@mock_dynamodb
def test_get_record_by_id():
    "Test get_record_by_id method"
    table = create_mock_dynamodb()
    questionnaires_record = build_mock_questionnaires_item()
    table.put_item(Item=questionnaires_record, TableName=service.TABLE_NAME)
    response = service.get_record_by_id(mock_id)
    assert response["Item"]["id"] == mock_id
    assert response["Item"]["active"] == mock_active
    assert response["Item"]["createdBy"] == mock_created_by
    assert response["Item"]["createdDateTime"] == mock_timestamp_created
    assert response["Item"]["lookup_field"] == mock_lookup_field
    assert response["Item"]["managingOrganization"] == mock_managing_organisation
    assert response["Item"]["modifiedBy"] == mock_modified_by
    assert response["Item"]["modifiedDateTime"] == mock_timestamp_modified
    assert response["Item"]["name"] == mock_name
    assert response["Item"]["Address"][0]["city"] == mock_city
    assert response["Item"]["Address"][0]["country"] == mock_country
    assert response["Item"]["Address"][0]["line"][0] == mock_line_1
    assert response["Item"]["Address"][0]["line"][1] == mock_line_2
    assert response["Item"]["Address"][0]["postalCode"] == mock_postcode
    assert response["Item"]["position"]["latitude"] == mock_lat
    assert response["Item"]["position"]["longitude"] == mock_long


@mock_dynamodb
def test_get_missing_record_by_id():
    "Test get_record_by_id method"
    create_mock_dynamodb()
    response = service.get_record_by_id(mock_id)
    assert ("Item" in response) is False
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_dynamodb
def test_add_record():
    "Test add record method - eg used by POST"
    table = create_mock_dynamodb()
    # check record with id does not already exist
    response = table.get_item(Key={"id": mock_post_id})
    assert ("Item" in response) is False
    # build record to add
    questionnaires_record = build_mock_questionnaires_item()
    questionnaires_record["active"] = mock_status_update
    questionnaires_record["id"] = mock_post_id
    service.add_record(questionnaires_record)
    response = table.get_item(Key={"id": mock_post_id})
    assert response["Item"]["id"] == mock_post_id
    assert response["Item"]["active"] == mock_status_update


@mock_dynamodb
def test_update_record():
    "Test update record method - eg used by PUT"
    table = create_mock_dynamodb()
    # Create and add a mock item to the table
    questionnaires_record = build_mock_questionnaires_item()
    table.put_item(Item=questionnaires_record, TableName=service.TABLE_NAME)
    response = service.get_record_by_id(mock_id)
    # check it has been saved correctly
    assert response["Item"]["id"] == mock_id
    assert response["Item"]["name"] == mock_name
    # update elements
    questionnaires_record["active"] = mock_status_update
    questionnaires_record["name"] = mock_updated_name
    service.update_record(questionnaires_record)
    # Verify that the item has been added successfully
    response = table.get_item(Key={"id": mock_id})
    assert response["Item"]["active"] == mock_status_update
    assert response["Item"]["name"] == mock_updated_name


@mock_dynamodb
def test_delete_record_by_id():
    "Test delete_record method first adding and then checking it exists"
    table = create_mock_dynamodb()
    questionnaires_record = build_mock_questionnaires_item()
    table.put_item(Item=questionnaires_record, TableName=service.TABLE_NAME)
    response = service.get_record_by_id(mock_id)
    assert response["Item"]["id"] == mock_id
    service.delete_record(mock_id)
    response = table.get_item(Key={"id": mock_id})
    assert ("Item" in response) is False


@mock_dynamodb
def test_delete_missing_record():
    "Test delete_record method if no  record exists"
    response = service.delete_record(mock_id)
    assert response == {}
