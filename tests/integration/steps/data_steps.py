from behave import given, then
from assertpy import assert_that
from utilities import dynamodb
from utilities.config_reader import read_config
import csv
import os


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
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")  # Specify the delimiter (usually a comma)
        headers = next(csv_reader)
        column_count = len(headers)
        # Convert csv_reader to a list so we can iterate over it multiple times
        rows = list(csv_reader)
        row_count = len(rows)
        print("The name of the file is:", file_name)
        print("The number of rows is: ", row_count)
        print("The headers are", headers)
        print("The number of columns is: ", column_count)
        print("Each row has the folowing data: ")
        # Iterate through each row in the CSV file
        for row in rows:
            print(row)
