from behave import given, then, step
import requests
from assertpy import assert_that
import json
from utilities import dynamodb


@given("I request data for {params} from {resource_name}")
def send_request_with_params(context, params, resource_name):
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    context.response = requests.get(url, params)


@given("I send a request to the resource {resource_name}")
def send_arequest(context, resource_name):
    context.response = requests.get(context.URL + "/" + resource_name + "?id=1")


@given("I post a request to the resource {resource_name}")
def send_request(context, resource_name):
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    with open("data_json/location_post_body.json") as json_file:
        json_data = json.load(json_file)
    print(json_file)
    context.response = requests.post(url, json=json_data)


@then("I receive a status code {status_code} in response")
def status_code(context, status_code):
    assert_that(context.response.status_code).is_equal_to(int(status_code))


@then("I can find data for id {id} in the dynamoDB table")
def dynamob_get(context, id):
    table_name = context.resource_name + "-" + context.workspace
    dynamodb.get_record_by_id(table_name, id)


@given("I can delete data for id {id} in the dynamoDB table {resource_name}")
def dynamob_delete(context, id, resource_name):
    table_name = resource_name + "-" + context.workspace
    dynamodb.get_record_by_id(table_name, id)


@given("I delete location data in the dynamoDB table")
def dynamob_post(context):
    table_name = context.resource_name + "-" + context.workspace
    dynamodb.add_record_from_file(table_name)


@step("I receive the message {message_text} in response")
def response_msg(context, message_text):
    response_content = context.response.text
    assert_that(str(response_content)).is_equal_to(str(message_text))


@then("I receive a field {fielddata} in response")
def fielddata(context, fielddata):
    response_dict = context.response.json()
    print(json.dumps(response_dict, indent=8, sort_keys=True))
