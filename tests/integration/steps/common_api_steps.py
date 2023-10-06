from behave import given, then, step

import requests
from assertpy import assert_that


@given("I send a request to the resource {resource_name}")
def send_request(context, resource_name):
    context.response = requests.get(context.URL + "/" + resource_name)


@then("I receive a status code {status_code} in response")
def status_code(context, status_code):
    assert_that(context.response.status_code).is_equal_to(int(status_code))


@step("I receive the message {message_text} in response")
def response_msg(context, message_text):
    response_content = context.response.text
    assert_that(str(response_content)).is_equal_to(str(message_text))
