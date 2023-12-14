from utilities.api import get_url
import json
import os.path


# -- BEHAVE HOOKS:
def before_scenario(context, scenario):
    print("\nbefore scenario executed")
    userdata = context.config.userdata
    context.workspace = userdata.get("workspace")
    context.apigateway = userdata.get("apigateway")
    configfile = userdata.get("configfile", "config_dev.json")
    if os.path.exists(configfile):
        assert configfile.endswith(".json")
        more_userdata = json.load(open(configfile))
        context.config.update_userdata(more_userdata)
    # TODO feed in env
    get_url(context)
