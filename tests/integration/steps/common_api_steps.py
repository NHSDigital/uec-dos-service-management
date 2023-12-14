from behave import given, then, step
import requests
from assertpy import assert_that
import json
from utilities import dynamodb


@given("I request {params} from {resource_name}")
def send_request_with_params(context, params, resource_name):
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    context.response = requests.get(url, params)


@given("I send a request to the resource {resource_name}")
def send_request(context, resource_name):
    context.response = requests.get(context.URL + "/" + resource_name + "?id=1")


@then("I receive a status code {status_code} in response")
def status_code(context, status_code):
    # response_dict = context.response.json()
    # print(json.dumps(response_dict, indent=8, sort_keys=True))
    table_name = context.resource_name + "-" + context.workspace
    print(table_name)
    dynamodb.get_record_by_id(table_name, 1)
    # assert_that(context.response.status_code).is_equal_to(int(status_code))


@step("I receive the message {message_text} in response")
def response_msg(context, message_text):
    response_content = context.response.text
    assert_that(str(response_content)).is_equal_to(str(message_text))


@then("I receive a field {fielddata} in response")
def fielddata(context, fielddata):
    response_dict = context.response.json()
    print(json.dumps(response_dict, indent=8, sort_keys=True))
