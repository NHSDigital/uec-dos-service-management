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

echo "Current terraform workspace is --> $TERRAFORM_WORKSPACE_NAME"
echo "Terraform state S3 bucket name is --> $TERRAFORM_BUCKET_NAME"
echo "Terraform state lock DynamoDB table is --> $TERRAFORM_LOCK_TABLE"


# Delete terraform state for current terraform workspace & echo results following deletion

deletion_output=$(aws s3 rm s3://$TERRAFORM_BUCKET_NAME/env:/ --recursive --exclude "*" --include "$TERRAFORM_WORKSPACE_NAME/*" 2>&1)

if [ -n "$deletion_output" ]; then
    echo "Sucessfully deleted Terraform State file for the following workspace --> $TERRAFORM_WORKSPACE_NAME"
else
    echo "Terraform State file not found for deletion or deletion failed for the following workspace --> $TERRAFORM_WORKSPACE_NAME"
fi

# Check if Terraform State Lock item exists before deletion,delete terraform state lock for current terraform workspace & echo results

existing_item=$(aws dynamodb get-item \
    --table-name "$TERRAFORM_LOCK_TABLE" \
    --key '{"LockID": {"S": "'${TERRAFORM_BUCKET_NAME}'/env:/'${TERRAFORM_WORKSPACE_NAME}'/application/terraform.state-md5"}}' \
    2>&1)

aws dynamodb delete-item \
    --table-name "$TERRAFORM_LOCK_TABLE" \
    --key '{"LockID": {"S": "'${TERRAFORM_BUCKET_NAME}'/env:/'${TERRAFORM_WORKSPACE_NAME}'/application/terraform.state-md5"}}'

after_deletion=$(aws dynamodb get-item \
    --table-name "$TERRAFORM_LOCK_TABLE" \
    --key '{"LockID": {"S": "'${TERRAFORM_BUCKET_NAME}'/env:/'${TERRAFORM_WORKSPACE_NAME}'/application/terraform.state-md5"}}' \
    2>&1)

if [[ -n "$existing_item" && -z "$after_deletion" ]]; then
    echo "Sucessfully deleted Terraform State Lock file for the following workspace --> $TERRAFORM_WORKSPACE_NAME"
else
    echo "Terraform state Lock file not found for deletion or deletion failed for the following workspace --> $TERRAFORM_WORKSPACE_NAME"
fi
