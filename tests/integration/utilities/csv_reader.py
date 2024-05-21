from utilities.config_reader import read_config
import csv


def get_csv_data(filename):
    # Open the CSV file in read mode
    file_name = read_config("csv_files", filename)
    with open(file_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        # next(csv_reader)
        rows = list(csv_reader)
        return rows


def csv_row_count(file_name):
    row_count = len(get_csv_data(file_name))
    return row_count


def csv_column_count(file_name):
    column_count = len(get_csv_data(file_name)[0])
    return column_count


def csv_headers(file_name):
    csv_headers = get_csv_data(file_name)[0]
    return csv_headers


def assert_cell_value(file_name):
    col_index = get_csv_data(file_name)[0].index("some_value")
    # Get the specific cell value
    cell_value = get_csv_data(file_name)[1][col_index]
    return cell_value
