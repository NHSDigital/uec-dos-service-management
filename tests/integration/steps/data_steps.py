from behave import given, then
from assertpy import assert_that
from utilities import dynamodb
from utilities.config_reader import read_config
import csv


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


@given(
    "I have the following csv file {file_name}, I can retrieve the data within the file"
)
def read_csv_data(context, file_name):
    # Open the CSV file in read mode
    with open("data_csv/{file_name}.csv", "r") as csv_file:
        csv_reader = csv.reader(
            csv_file, delimiter=","
        )  # Specify the delimiter (usually a comma)

    # Iterate through each row in the CSV file
    for row in csv_reader:
        print(row)  # Print each row (you can process the data as needed)
