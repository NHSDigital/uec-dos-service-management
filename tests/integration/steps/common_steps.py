from behave import then, when
import requests
from assertpy import assert_that
import json
from utilities.config_reader import read_config
import allure


@when("I request data for {params} from {resource_name}")
def send_get_with_params(context, params, resource_name):
    allure.dynamic.description("Workspace: " + context.workspace)
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    context.response = requests.get(url, params)



@when("I delete data for id {id} from the resource {resource_name}")
def send_delete_with_params(context, id, resource_name):
    allure.dynamic.description("Workspace: " + context.workspace)
    body = {}
    body["id"] = id
    json_body = json.dumps(body)
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    context.response = requests.delete(url, data=json_body)


@when("I post the json {file_name} to the resource {resource_name}")
def send_post_with_file(context, file_name, resource_name):
    allure.dynamic.description("Workspace: " + context.workspace)
    body = read_config("json_schema", file_name)
    context.resource_name = resource_name
    url = context.URL + "/" + resource_name
    with open(body) as json_file:
        json_data = json.load(json_file)
    context.response = requests.post(url, json=json_data)


@then("I receive a status code {status_code} in response")
def status_code(context, status_code):
    allure.dynamic.description("Workspace: " + context.workspace)
    assert_that(context.response.status_code).is_equal_to(int(status_code))


@then("I receive data for id {id} in the response")
def response_id_get(context, id):
    allure.dynamic.description("Workspace: " + context.workspace)
    response = context.response.json()
    assert_that(response["Item"]["id"]).is_equal_to(id)
