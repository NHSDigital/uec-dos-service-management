#! /bin/bash

# fail on first error
set -e
# functions
source ./scripts/project-common.sh
source ./scripts/functions/terraform-functions.sh
source ./scripts/functions/git-functions.sh

export_terraform_workspace_name
# check exports have been done
EXPORTS_SET=0

if [ -z "$TERRAFORM_WORKSPACE_NAME" ] ; then
  echo Set TERRAFORM_WORKSPACE_NAME
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

echo "current terraform workspace is $TERRAFORM_WORKSPACE_NAME"

# delete terraform state for current terraform workspace

aws s3 rm s3://nhse-dev-uec-dos-service-management-terraform-state/env:/ --recursive --exclude "*" --include "$TERRAFORM_WORKSPACE_NAME/*"
echo "Sucessfully deleted terraform state for the following workspace $TERRAFORM_WORKSPACE_NAME"

# delete terraform state lock for current terraform workspace
aws dynamodb delete-item \
    --table-name "nhse-dev-uec-dos-service-management-terraform-state-lock" \
    --key '{"LockID": {
    "S": "nhse-dev-uec-dos-service-management-terraform-state/env:/'${TERRAFORM_WORKSPACE_NAME}'/application/terraform.state-md5"}}'
echo "Sucessfully deleted terraform state lock for the following workspace $TERRAFORM_WORKSPACE_NAME"
