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

    # data = {
    #     "id": post_data["id"],
    #     "HospitalName": post_data["HospitalName"],
    #     "HospitalLocation": post_data["HospitalLocation"],
    # }

    print(post_data)
    # service.add_record(data)

    return {"statusCode": 200, "body": "Item Added Successfully"}


# Get using query string approach
@app.get("/locations")
def get_locations():
    print("get")
    # print(app.current_event)
    l_id = app.current_event.get_query_string_value(name="id", default_value="")
    # print("Get l_id record..." + l_id)
    # print(type(l_id))
    response = service.get_record_by_id(l_id)
    # print(type(response))
    print(response)
    print("here")
    return response
    # return {"statusCode": 200, "body": response}


@app.put("/locations")
def update_locations():
    print("put")
    put_data: dict = app.current_event.json_body
    service.update_record(
        put_data["id"], put_data["HospitalName"], put_data["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}


# original
@app.delete("/locations")
def delete_locations():
    print("del")
    print(type(app.current_event))
    print(app.current_event)
    print(app.current_event.decoded_body)
    delete_data: dict = app.current_event.json_body
    print("Delete locations record...")
    print(delete_data)
    print(type(delete_data))
    l_id = delete_data["id"]
    print(l_id)
    response = service.delete_record(l_id)
    # response = {"Item": {'id': '2690664379947884'}}
    print(type(response))
    print(response)
    print("deleted and on")
    return response
    # return {"statusCode": 200, "body": "Item Deleted Successfully"}


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
