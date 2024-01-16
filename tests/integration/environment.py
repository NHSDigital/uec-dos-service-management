from utilities.api import get_url


# -- BEHAVE HOOKS:
def before_scenario(context, scenario):
    print("\nbefore scenario executed")
    userdata = context.config.userdata
    context.apigateway = userdata.get("apigateway")
    if userdata.get("workspace") != "default":
        context.workspace = "-" + userdata.get("workspace")
    else:
        context.workspace = ""
    get_url(context)
