#! /bin/bash

PROGRAM_CODE="${PROGRAM_CODE:-"nhse-uec"}"
AWS_REGION="${AWS_REGION:-"eu-west-2"}"
INFRASTRUCTURE_DIR="${INFRASTRUCTURE_DIR:-"infrastructure"}"
TERRAFORM_DIR="${TERRAFORM_DIR:-"$INFRASTRUCTURE_DIR/stacks"}"
ACCOUNT_TYPE="${ACCOUNT_TYPE:-""}"

export TERRAFORM_BUCKET_NAME="nhse-$ACCOUNT_TYPE-$TF_VAR_repo_name-terraform-state"  # globally unique name
export TERRAFORM_LOCK_TABLE="nhse-$ACCOUNT_TYPE-$TF_VAR_repo_name-terraform-state-lock"

function terraform-initialise {
    STACK=$1
    ENVIRONMENT=$2
    TERRAFORM_USE_STATE_STORE=$3
    TERRAFORM_STATE_STORE=$TERRAFORM_BUCKET_NAME
    TERRAFORM_STATE_LOCK=$TERRAFORM_LOCK_TABLE
    TERRAFORM_STATE_KEY=$STACK/terraform.state

    if [[ "$TERRAFORM_USE_STATE_STORE" =~ ^(false|no|n|off|0|FALSE|NO|N|OFF) ]]; then
      terraform init
    else
      terraform init \
          -backend-config="bucket=$TERRAFORM_STATE_STORE" \
          -backend-config="dynamodb_table=$TERRAFORM_STATE_LOCK" \
          -backend-config="encrypt=true" \
          -backend-config="key=$TERRAFORM_STATE_KEY" \
          -backend-config="region=$AWS_REGION"
    fi
}

function terraform-init-migrate {
    STACK=$1
    ENVIRONMENT=$2
    TERRAFORM_USE_STATE_STORE=$3
    TERRAFORM_STATE_STORE=$TERRAFORM_BUCKET_NAME
    TERRAFORM_STATE_LOCK=$TERRAFORM_LOCK_TABLE
    TERRAFORM_STATE_KEY=$STACK/terraform.state

    terraform init -migrate-state -force-copy \
        -backend-config="bucket=$TERRAFORM_STATE_STORE" \
        -backend-config="dynamodb_table=$TERRAFORM_STATE_LOCK" \
        -backend-config="encrypt=true" \
        -backend-config="key=$TERRAFORM_STATE_KEY" \
        -backend-config="region=$AWS_REGION"

}
