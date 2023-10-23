import os


def get_table_name(table_name):
    workspace_table_name = table_name
    if os.getenv("WORKSPACE") is not None and os.getenv("WORKSPACE") != "":
        workspace_table_name = table_name + "-" + os.getenv("WORKSPACE")
    return workspace_table_name
