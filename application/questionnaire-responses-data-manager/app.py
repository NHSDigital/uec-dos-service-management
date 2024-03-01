import os
import service
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

app = APIGatewayRestResolver()

# Auto resolves the type of request comming through and sets APIGatewayRestResolver
# fields

log_level = os.environ.get("LOG_LEVEL", "info")
logger = Logger(service="questionnaire_responses", level=log_level)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info(event)
    logger.debug(event)
    return app.resolve(event, context)


@app.post("/questionnaire_responses")
def create_questionnaireresponses():
    post_data: dict = app.current_event.json_body
    response = service.add_record(post_data)
    return response


# Get using query string approach
@app.get("/questionnaire_responses")
def get_questionnaireresponses():
    qr_id = app.current_event.get_query_string_value(name="id", default_value="")
    response = service.get_record_by_id(qr_id)
    return response


@app.put("/questionnaire_responses")
def update_questionnaireresponses():
    put_data: dict = app.current_event.json_body
    response = service.update_record(put_data)
    return response


@app.delete("/questionnaire_responses")
def delete_questionnaireresponses():
    delete_data: dict = app.current_event.json_body
    qr_id = delete_data["id"]
    response = service.delete_record(qr_id)
    return response
