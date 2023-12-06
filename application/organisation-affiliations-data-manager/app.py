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
        "HospitalName": post_data["HospitalName"],
        "HospitalLocation": post_data["HospitalLocation"],
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
    oa_id = app.current_event.get_query_string_value(name="id", default_value="")
    print("Get oa_id record..." + oa_id)
    response = service.get_record_by_id(oa_id)
    return {"statusCode": 200, "body": response}


@app.put("/organisation_affiliations")
def update_organisationaffiliationss():
    put_data: dict = app.current_event.json_body
    service.update_record(
        put_data["id"], put_data["HospitalName"], put_data["HospitalLocation"]
    )
    return {"statusCode": 200, "body": "Item Updated Successfully"}


@app.delete("/organisation_affiliations")
def delete_organisationaffiliationss():
    delete_data: dict = app.current_event.json_body
    print("Delete organisationaffiliations record...")
    oa_id = delete_data["id"]
    service.delete_record(oa_id)
    return {"statusCode": 200, "body": "Item Deleted Successfully"}
