from utilities.api import get_url


# -- BEHAVE HOOKS:
def before_scenario(context, scenario):
    print("\nbefore scenario executed")
    userdata = context.config.userdata
    context.workspace = userdata.get("workspace")
    context.apigateway = userdata.get("apigateway")
    get_url(context)
