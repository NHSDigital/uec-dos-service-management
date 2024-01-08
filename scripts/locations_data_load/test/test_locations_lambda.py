import uuid
import datetime


def test_generate_random_id():
    assert str(uuid.uuid4().int)[0:16] != ""


def test_get_formatted_datetime():
    assert datetime.datetime.now() != ""


line = "random text"


def test_capitalize_line():
    response = line.title()
    assert response != line


# address_item = [{
#     "address": [{
#         "line": ["CERTAIN", "PHARMACY", "ADDRESS"],
#         "city": "CITY",
#         "district": "CERTAIN DISTRICT",
#         "postalCode": "A11 11AE",
#         "country": "ENGLAND",
#     }]}]


# def test_capitalize_address_item(address_item):
#     response = locations_lambda.capitalize_address_item(address_item)
#     assert response.capitalized_item["city"] == "City"


# locations_lambda.data_exists
# locations_lambda.update_records
# locations_lambda.write_to_json
# locations_lambda.process_organizations
# locations_lambda.read_excel_values
