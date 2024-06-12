from behave import given, then
from assertpy import assert_that
from utilities import dynamodb, csv_reader
from utilities.config_reader import read_config
import os
import boto3


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


@given("I have the following csv file {file_name} I have {rowcount} rows")
def count_csv_rows(context, file_name, rowcount):
    row_count = str(csv_reader.csv_row_count(file_name))
    assert row_count == rowcount


@given("I have the following csv file {file_name}, I can assert that the file exists")
def assert_file_exists(context, file_name):
    filename = read_config("csv_files", file_name)
    file_name = os.path.basename(filename)
    assert os.path.isfile(filename)


@given("I have the following csv file {file_name} I have {columncount} columns")
def count_csv_columns(context, file_name, columncount):
    column_count = str(csv_reader.csv_column_count(file_name))
    assert column_count == columncount


@given("I have the following csv file {file_name} I have the correct headers")
def assert_csv_headers(context, file_name):
    csv_headers = str(csv_reader.csv_headers(file_name))
    headers = "['test_case', 'some_value', 'some_other_value']"
    assert csv_headers == headers


@given(
    "I have the following csv file {file_name} I can assert the correct value in a cell"
)
def assert_csv_cell_value(context, file_name):
    csv_cell_value = str(csv_reader.assert_cell_value(file_name))
    cell_value = "value 13"
    assert csv_cell_value == cell_value


@given(
    "I want to upload the file {file_name} to the s3 bucket {bucket}"
)
def put_s3_file(context, file_name, bucket):
    print(bucket)
    filename = read_config("s3_files", file_name)
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).upload_file(filename, filename)


@given("I want to retreive the file {file_name} from the s3 bucket {bucket}")
def get_s3_file(context, bucket, file_name):
    s3 = boto3.client("s3")
    filename = read_config("s3_files", file_name)
    response = s3.get_object(Bucket=bucket, Key=filename)
    file = response["Body"].read().decode("utf-8")
    print("The contents of the s3 file is: ", file, "\n")


@given("I want to delete the file {file_name} from the s3 bucket {bucket}")
def delete_s3_file(context, bucket, file_name):
    s3 = boto3.resource("s3")
    filename = read_config("s3_files", file_name)
    s3.Object(bucket, filename).delete()
