from utilities.api import get_url


# -- BEHAVE HOOKS:
def before_scenario(context, scenario):
    userdata = context.config.userdata
    context.env = userdata.get("env")
    context.apigateway = userdata.get("apigateway")
    if userdata.get("workspace") != "default":
        context.workspace = "-" + userdata.get("workspace")
    else:
        context.workspace = ""
    get_url(context)
