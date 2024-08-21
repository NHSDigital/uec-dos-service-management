from behave import given, then
from assertpy import assert_that
from utilities import csv_reader, s3, directories
from utilities.config_reader import read_config


@given("I have a csv file called {file_name}")
def assert_file_exists(context, file_name):
    context.file_name = read_config("csv_files", file_name)


@then("the file contains {rowcount} rows")
def count_csv_rows(context, rowcount):
    row_count = str(csv_reader.csv_row_count(context))
    assert_that(row_count).is_equal_to(rowcount)


@then("the file contains {columncount} columns")
def count_csv_columns(context, columncount):
    column_count = str(csv_reader.csv_column_count(context))
    assert_that(column_count).is_equal_to(columncount)


@then("the file contains the correct headers {headers}")
def assert_csv_headers(context, headers):
    csv_headers = str(csv_reader.csv_headers(context))
    assert_that(csv_headers).is_equal_to(headers)


@then("the file contains {value} in row {rownum} column {colnum}")
def assert_csv_cell_value(context, value, rownum, colnum):
    csv_cell_value = str(csv_reader.assert_cell_value(context, rownum, colnum))
    assert_that(csv_cell_value).is_equal_to(value)


@given("I want to upload the file {file_name} to the s3 bucket")
def put_s3_file(context, file_name):
    context.file_name = file_name + ".csv"
    filepath = read_config("csv_files", file_name)
    s3.put_object(context, filepath, context.file_name)


@then("I can download the file {file_name} from the s3 bucket")
def download_s3_file(context, file_name):
    downloadfile = file_name
    directories.create_folder("downloads")
    context.file_name = "downloads/" + downloadfile
    s3.download_object(context, context.file_name, downloadfile)


@then("I can retrieve the file {file_name} from the s3 bucket")
def get_s3_file(context, file_name):
    file_name = s3.get_object(context, file_name)


@then("I can delete the file {file_name} from the s3 bucket")
def delete_s3_file(context, file_name):
    s3.delete_object(context, file_name)
