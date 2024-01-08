from locations_data_load import locations_lambda
# from locations_lambda import read_ods_api
# from locations_lambda import api_endpoint

from unittest.mock import patch
#from nose.tools import assert_is_not_none


def test_generate_random_id():
    response = locations_lambda.generate_random_id()
    assert response != ""


def test_get_formatted_datetime():
    response = locations_lambda.get_formatted_datetime()
    assert response != ""


# @patch("locations_lambda.requests.get")
# def test_read_ods_api(self):

#     with patch ('locations_lambda.requests.get') as mock_get:
#         # Configure the mock to return a response with an OK status code.
#         mock_get.return_value.status_code = 200

#         # Call the service, which will send a request to the server.
#         response = locations_lambda.read_ods_api(locations_lambda.api_endpoint)

#         # If the request is sent successfully, then I expect a response to be returned.
#         self.assertEqual(response.status_code, 200)


line = "random text"
def test_capitalize_line():
    response = locations_lambda.capitalize_line(line)
    assert response == line.title()


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
