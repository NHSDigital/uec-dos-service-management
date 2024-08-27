from behave import given, then
from assertpy import assert_that
from utilities import dynamodb
from utilities.config_reader import read_config


@given("I reset the data by deleting id {id} in the dynamoDB table {resource_name}")
def dynamodb_delete(context, id, resource_name):
    table_name = resource_name + context.workspace
    dynamodb.delete_record_by_id(table_name, id)


@given(
    "I setup the data by inserting from file {file_name} into the dynamoDB table {resource_name}"
)
def dynamodb_add(context, file_name, resource_name):
    body = read_config("json_schema", file_name)
    table_name = resource_name + context.workspace
    dynamodb.add_record_from_file(table_name, body)


@then("I can retrieve data for id {id} in the dynamoDB table")
def dynamodb_get(context, id):
    table_name = context.resource_name + context.workspace
    response = dynamodb.get_record_by_id(table_name, id)
    assert_that(response["Item"]["id"]).is_equal_to(id)


@then("data for id {id} in the dynamoDB table has been deleted")
def dynamodb_check_delete(context, id):
    table_name = context.resource_name + context.workspace
    response = dynamodb.get_record_by_id(table_name, id)
    assert_that(
        response["ResponseMetadata"]["HTTPHeaders"]["content-length"]
    ).is_equal_to("2")
    assert_that(response).does_not_contain("Item")
