import csv


def get_csv_data(context):
    with open(context.file_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        rows = list(csv_reader)
    return rows


def csv_row_count(context):
    row_count = len(get_csv_data(context))
    return row_count


def csv_column_count(context):
    column_count = len(get_csv_data(context)[0])
    return column_count


def csv_headers(context):
    csv_headers = get_csv_data(context)[0]
    return csv_headers


def assert_cell_value(context, rownum, colnum):
    rownum = int(rownum)
    colnum = int(colnum)
    cell_value = get_csv_data(context)[rownum][colnum]
    return cell_value
