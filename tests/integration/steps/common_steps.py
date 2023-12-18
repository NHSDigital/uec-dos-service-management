from behave import given, then, when
import requests
from assertpy import assert_that
import json
from config import config_dev


@given("I request data for {params} from {resource_name}")
def send_get_with_params(context, params, resource_name):
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    context.response = requests.get(url, params)


@when("I delete data for {params} from the resource {resource_name}")
def send_delete_with_params(context, params, resource_name):
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    context.response = requests.delete(url, json=params)


@given("I post a request to the resource {resource_name}")
def send_post(context, resource_name):
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    with open("data_json/location_post_body.json") as json_file:
        json_data = json.load(json_file)
    context.response = requests.post(url, json=json_data)


@when("I post the json {file_name} to the resource {resource_name}")
def send_post_with_file(context, file_name, resource_name):
    body = config_dev.locations_body
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    # with open("data_json/location_post_body.json") as json_file:
    with open(body) as json_file:
        json_data = json.load(json_file)
    context.response = requests.post(url, json=json_data)


@then("I receive a status code {status_code} in response")
def status_code(context, status_code):
    assert_that(context.response.status_code).is_equal_to(int(status_code))


@then("I receive the message {message_text} in response")
def response_msg(context, message_text):
    response_content = context.response.text
    assert_that(str(response_content)).is_equal_to(str(message_text))


@then("I receive a field {fielddata} in response")
def fielddata(context, fielddata):
    response_dict = context.response.json()
    print(json.dumps(response_dict, indent=8, sort_keys=True))
