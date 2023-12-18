from behave import given, then
from utilities import dynamodb
from config import config_dev


@given("I reset the data by deleting id {id} in the dynamoDB table {resource_name}")
def dynamodb_delete(context, id, resource_name):
    table_name = resource_name + "-" + context.workspace
    dynamodb.delete_record_by_id(table_name, id)


@given(
    "I setup the data by inserting from file into the dynamoDB table {resource_name}"
)
def dynamodb_add(context, resource_name):
    body = config_dev.locations_body
    table_name = resource_name + "-" + context.workspace
    dynamodb.add_record_from_file(table_name, body)


@then("I can retrieve data for id {id} in the dynamoDB table")
def dynamodb_get(context, id):
    table_name = context.resource_name + "-" + context.workspace
    dynamodb.get_record_by_id(table_name, id)
