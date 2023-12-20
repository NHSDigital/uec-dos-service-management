import service
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayRestResolver()


# Auto resolves the type of request comming through and sets APIGatewayRestResolver
# fields
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


@app.post("/locations")
def create_locations():
    print("post")
    print(app.current_event)
    post_data: dict = app.current_event.json_body
    response = service.add_record(post_data)
    return response


# Get using query string approach
@app.get("/locations")
def get_locations():
    print("get")
    # print(app.current_event)
    l_id = app.current_event.get_query_string_value(name="id", default_value="")
    response = service.get_record_by_id(l_id)
    return response


@app.put("/locations")
def update_locations():
    print("put")
    put_data: dict = app.current_event.json_body
    response = service.update_record(put_data)
    return response


# original
@app.delete("/locations")
def delete_locations():
    print("del")
    print(type(app.current_event))
    print(app.current_event)
    print(app.current_event.decoded_body)
    delete_data: dict = app.current_event.json_body
    l_id = delete_data["id"]
    response = service.delete_record(l_id)
    return response


# @app.delete("/locations")
# def delete_locations():
#     print("delete")
#     # l_id = app.current_event.get_query_string_value(name="id", default_value="")
#     print(app.current_event)
#     print(type(app.current_event))
#     # delete_data: dict = app.current_event.decoded_body
#     delete_data: dict = app.current_event.json_body
#     print(delete_data)
#     print("Delete locations record...")
#     print(type(delete_data))
#     l_id = delete_data["id"]
#     response = service.delete_record(l_id)
#     return response
#     # return {"statusCode": 200, "body": "Item Deleted Successfully"}
