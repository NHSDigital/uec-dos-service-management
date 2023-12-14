# from utilities import secrets
from utilities.api_gateway import ApiGatewayToService


def get_url(context):
    # userdata = context.config.userdata
    # workspace = userdata.get("workspace")

    # get the api gateway name env var and then the api gateway id
    apigateway_name = context.apigateway
    if context.workspace != "default":
        apigateway_name = apigateway_name + "-" + context.workspace
    agts = ApiGatewayToService()
    apigatewayid = agts.get_rest_api_id(apigateway_name)

    # set the URL for the api-gateway stage identified by the workspace and api gateway id
    context.URL = (
        "https://" + str(apigatewayid) + ".execute-api.eu-west-2.amazonaws.com/default"
    )
