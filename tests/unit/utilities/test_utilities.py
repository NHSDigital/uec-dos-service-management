import os
from chalicelib.common import utilities

from unittest import mock

test_table_name = "TEST-TABLE"

workspace_env_name = "WORKSPACE"
workspace_env_value = "DR-999"
workspace_env_default_value = ""


def test_get_table_name_with_no_environment_var():
    "Test get_table_name method without WORKSPACE environment variable set"
    table_name = utilities.get_table_name(test_table_name)
    assert table_name == test_table_name


def test_get_table_name_with_no_environment_var_empty_table_name():
    "Test get_table_name method without WORKSPACE environment variable set and empty table name"
    table_name = utilities.get_table_name("")
    assert table_name == ""


@mock.patch.dict(os.environ, {workspace_env_name: workspace_env_default_value})
def test_get_table_name_with_environment_var_empty():
    "Test get_table_name method with WORKSPACE environment variable empty"
    table_name = utilities.get_table_name(test_table_name)
    assert table_name == test_table_name


@mock.patch.dict(os.environ, {workspace_env_name: workspace_env_value})
def test_get_table_name_with_environment_var_set():
    "Test get_table_name method with WORKSPACE environment variable set"
    table_name = utilities.get_table_name(test_table_name)
    assert table_name == test_table_name + "-" + workspace_env_value


@mock.patch.dict(os.environ, {workspace_env_name: workspace_env_value})
def test_get_table_name_with_environment_var_set_empty_table_name():
    "Test get_table_name method with WORKSPACE environment variable set with no table name set"
    table_name = utilities.get_table_name("")
    assert table_name == "-" + workspace_env_value
