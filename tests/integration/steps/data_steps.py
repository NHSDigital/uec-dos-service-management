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
        csv_reader = csv.reader(
            csv_file, delimiter=","
        )  # Specify the delimiter (usually a comma)
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
        print(row_count)


@given("I have the following csv file {file_name}, I can assert that the file exists")
def assert_file_exists(context, file_name):
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    assert os.path.isfile(filename)


@given(
    "I have the following csv file {file_name}, I can assert that the number of rows in the file is correct"
)
def assert_row_count(context, file_name):
    # Open the CSV file in read mode
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)
        rows = list(csv_reader)
        row_count = len(rows)
        assert row_count == 4


@given(
    "I have the following csv file {file_name}, I can assert that the number of columns in the file is correct"
)
def assert_column_count(context, file_name):
    # Open the CSV file in read mode
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        headers = next(csv_reader)
        column_count = len(headers)
        assert column_count == 3


@given(
    "I have the following csv file {file_name}, I can assert that the headers in the file are correct"
)
def assert_file_headers(context, file_name):
    # Open the CSV file in read mode
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        headers = next(csv_reader)
        assert headers == ["test_case", "some_value", "some_other_value"]


@given(
    "I have the csv file {file_name}, I can assert file has the correct value in row 2 of the some value column"
)
def assert_cell_value(context, file_name):
    # Open the CSV file in read mode
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        headers = next(csv_reader)
        rows = list(csv_reader)
        # Get the index of the column
        col_index = headers.index("some_value")
        # Get the specific cell value
        cell_value = rows[1][col_index]
        assert cell_value == "value 16"
