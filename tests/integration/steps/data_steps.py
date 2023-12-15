from behave import given, then

# from assertpy import assert_that
from utilities import dynamodb


@given("I can delete data for id {id} in the dynamoDB table {resource_name}")
def dynamodb_delete(context, id, resource_name):
    table_name = resource_name + "-" + context.workspace
    dynamodb.delete_record_by_id(table_name, id)


@given("I add location data to the dynamoDB table")
def dynamodb_post(context):
    table_name = context.resource_name + "-" + context.workspace
    dynamodb.add_record_from_file(table_name)


@then("I can get data for id {id} in the dynamoDB table")
def dynamodb_get(context, id):
    table_name = context.resource_name + "-" + context.workspace
    dynamodb.get_record_by_id(table_name, id)
