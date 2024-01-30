import service
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayRestResolver()


# Auto resolves the type of request coming through and sets APIGatewayRestResolver
# fields
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


@app.post("/organisation_affiliations")
def create_organisationaffiliations():
    post_data: dict = app.current_event.json_body
    response = service.add_record(post_data)
    return response


# Get using query string approach
@app.get("/organisation_affiliations")
def get_organisationaffiliations():
    oa_id = app.current_event.get_query_string_value(name="id", default_value="")
    response = service.get_record_by_id(oa_id)
    return response


@app.put("/organisation_affiliations")
def update_organisationaffiliations():
    put_data: dict = app.current_event.json_body
    response = service.update_record(put_data, "temp", "temp")
    return response


@app.delete("/organisation_affiliations")
def delete_organisationaffiliationss():
    delete_data: dict = app.current_event.json_body
    oa_id = delete_data["id"]
    response = service.delete_record(oa_id)
    return response
