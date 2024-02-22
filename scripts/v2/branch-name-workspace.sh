#!/bin/bash

# fail on first error
set -e
# functions
source ./scripts/v2/project-common.sh
source ./scripts/v2/functions/terraform-functions.sh
source ./scripts/v2/functions/git-functions.sh

export_terraform_workspace_name
echo $TERRAFORM_WORKSPACE_NAME
