import service
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayRestResolver()

# Auto resolves the type of request comming through and sets APIGatewayRestResolver
# fields
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)

@app.post("/organisation_affiliations")
def create_organisationaffiliations():
    post_data: dict = app.current_event.json_body

    data = {
        "id": post_data["id"],
        "hospitalName": post_data["hospitalname"],
        "hospitalLocation": post_data["hospitallocation"],
    }

    print(data)
    service.add_record(data)

    return {"statusCode": 200, "body": "Item Added Successfully"}

# Dynamic get using URL path rather than query string
# @app.get("/organisation_affiliations/<id>")
# def get_organisationaffiliations(id):
#     print("ID from Get: " + str(id))
#     print("Get hs_id record..." + id)
#     response = service.get_record_by_id(id)
#     return {"statusCode": 200, "body": response}


# Get using query string approach
@app.get("/organisation_affiliations")
def get_organisationaffiliations():
    hs_id = app.current_event.get_query_string_value(name="id", default_value="")
    print("Get hs_id record..." + hs_id)
    response = service.get_record_by_id(hs_id)
    return {"statusCode": 200, "body": response}



@app.put("/organisation_affiliations")
def update_organisationaffiliationss():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Updating organisation_affiliations record...")
    request = app.current_request.json_body
    service.update_record(
        request["id"], request["HospitalName"], request["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}


@app.delete("/organisation_affiliations")
def delete_organisationaffiliationss():
    #    request = app.current_request.json_body  // Required to get request from the API Gateway once it's set up.
    print("Delete organisationaffiliations record...")
    request = app.current_request.json_body
    hs_id = request["id"]
    service.delete_record(hs_id)

    return {"statusCode": 200, "body": "Item Deleted Successfully"}
