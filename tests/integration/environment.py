from utilities.api_gateway import ApiGatewayToService


# -- BEHAVE HOOKS:
def before_all(context):
    # get the workspace var that has been passed through from the integration-tests script
    userdata = context.config.userdata
    workspace = userdata.get("workspace")

    # get the api gateway name env var and then the api gateway id
    apigateway_name = userdata.get("apigateway")
    apigateway_name = apigateway_name + "-" + workspace
    agts = ApiGatewayToService()
    apigatewayid = agts.get_rest_api_id(apigateway_name)

    # set the URL for the api-gateway stage identified by the workspace and api gateway id
    context.URL = (
        "https://" + str(apigatewayid) + ".execute-api.eu-west-2.amazonaws.com/default"
    )
