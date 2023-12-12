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
    post_data: dict = app.current_event.json_body

    data = {
        "id": post_data["id"],
        "HospitalName": post_data["HospitalName"],
        "HospitalLocation": post_data["HospitalLocation"],
    }

    print(data)
    service.add_record(data)

    return {"statusCode": 200, "body": "Item Added Successfully"}


# Get using query string approach
@app.get("/locations")
def get_locations():
    l_id = app.current_event.get_query_string_value(name="id", default_value="")
    print("Get l_id record..." + l_id)
    response = service.get_record_by_id(l_id)
    return {"statusCode": 200, "body": response}


@app.put("/locations")
def update_locations():
    put_data: dict = app.current_event.json_body
    service.update_record(
    put_data["id"], put_data["HospitalName"], put_data["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}

@app.delete("/locations")
def delete_locations():
    delete_data: dict = app.current_event.json_body
    print("Delete locations record...")
    l_id = delete_data["id"]
    service.delete_record(l_id)
    return {"statusCode": 200, "body": "Item Deleted Successfully"}
