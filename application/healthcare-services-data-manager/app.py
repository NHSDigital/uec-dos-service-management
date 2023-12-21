import service
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayRestResolver()


# Auto resolves the type of request comming through and sets APIGatewayRestResolver
# fields


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


@app.post("/healthcare_services")
def create_healthcareservices():
    post_data: dict = app.current_event.json_body
    response = service.add_record(post_data)
    return response


# Get using query string approach
@app.get("/healthcare_services")
def get_healthcareservices():
    hs_id = app.current_event.get_query_string_value(name="id", default_value="")
    response = service.get_record_by_id(hs_id)
    return response


@app.put("/healthcare_services")
def update_healthcareservices():
    put_data: dict = app.current_event.json_body
    response = service.update_record(put_data)
    return response


@app.delete("/healthcare_services")
def delete_healthcareservices():
    delete_data: dict = app.current_event.json_body
    hs_id = delete_data["id"]
    response = service.delete_record(hs_id)
    return response
