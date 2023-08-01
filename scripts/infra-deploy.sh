#! /bin/bash
# You will need to export
# ACTION eg plan, apply, destroy
# STACK eg iam-policy
# ACCOUNT_TYPE eg dev,test
# ACCOUNT_PROJECT eg dos or cm

# clear out local state
# functions
source ./scripts/functions/terraform-functions.sh

export ACTION="${ACTION:-""}"               # The terraform action to execute
export STACK="${STACK:-""}"                 # The terraform stack to be actioned
export ACCOUNT_TYPE="${ACCOUNT_TYPE:-""}"     # The type of account being used - dev test
export ACCOUNT_PROJECT="${ACCOUNT_PROJECT:-""}"             # dos or cm
export USE_REMOTE_STATE_STORE="${USE_REMOTE_STATE_STORE:-true}"
# check exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above
if [ -z "$ACTION" ] ; then
  echo Set ACTION to terraform action one of plan apply or destroy
  EXPORTS_SET=1
fi

if [ -z "$STACK" ] ; then
  echo Set STACK to name of the stack to be planned, applied, destroyed
  EXPORTS_SET=1
fi

if [ -z "$ACCOUNT_TYPE" ] ; then
  echo Set ACCOUNT_TYPE type of ACCOUNT_TYPE - one of dev, test, preprod, prod
  EXPORTS_SET=1
else
  if [[ ! $ACCOUNT_TYPE =~ ^(dev|test|preprod|prod|security) ]]; then
      echo ACCOUNT_TYPE should be dev test preprod security or prod
      EXPORTS_SET=1
  fi
fi

if [ -z "$ACCOUNT_PROJECT" ] ; then
  echo Set ACCOUNT_PROJECT to dos or cm
  EXPORTS_SET=1
else
  if [[ ! "$ACCOUNT_PROJECT" =~ ^(dos|cm) ]]; then
      echo ACCOUNT_PROJECT should be dos or cm
      EXPORTS_SET=1
  fi
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

COMMON_TF_VARS_FILE="common.tfvars"
PROJECT_TF_VARS_FILE="$ACCOUNT_PROJECT-project.tfvars"
ENV_TF_VARS_FILE="$ACCOUNT_TYPE.tfvars"
echo "Preparing to run terraform $ACTION for stack $STACK for account type $ACCOUNT_TYPE and project $ACCOUNT_PROJECT"
ROOT_DIR=$PWD
# the directory that holds the stack to terraform
STACK_DIR=$PWD/$INFRASTRUCTURE_DIR/stacks/$STACK
# remove any previous local backend for stack
rm -rf "$STACK_DIR"/.terraform
rm -f "$STACK_DIR"/.terraform.lock.hcl
#  copy shared tf files to stack
if [[ "$USE_REMOTE_STATE_STORE" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON) ]]; then
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/remote/versions.tf "$STACK_DIR"
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/remote/locals.tf "$STACK_DIR"
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/remote/provider.tf "$STACK_DIR"
else
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/local/versions.tf "$STACK_DIR"
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/local/locals.tf "$STACK_DIR"
  cp "$ROOT_DIR"/"$INFRASTRUCTURE_DIR"/local/provider.tf "$STACK_DIR"
fi
# switch to target stack directory ahead of tf init/plan/apply
cd "$STACK_DIR" || exit
# init terraform
terraform-initialise "$STACK" "$ACCOUNT_TYPE" "$USE_REMOTE_STATE_STORE"
# plan
if [ -n "$ACTION" ] && [ "$ACTION" = 'plan' ] ; then
  terraform plan \
  -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$COMMON_TF_VARS_FILE \
  -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$PROJECT_TF_VARS_FILE \
  -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$ENV_TF_VARS_FILE
fi

if [ -n "$ACTION" ] && [ "$ACTION" = 'apply' ] ; then
  terraform apply -auto-approve \
    -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$COMMON_TF_VARS_FILE \
    -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$PROJECT_TF_VARS_FILE \
    -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$ENV_TF_VARS_FILE
fi

if [ -n "$ACTION" ] && [ "$ACTION" = 'destroy' ] ; then
  terraform destroy -auto-approve\
    -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$COMMON_TF_VARS_FILE \
    -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$PROJECT_TF_VARS_FILE \
    -var-file $ROOT_DIR/$INFRASTRUCTURE_DIR/$ENV_TF_VARS_FILE
fi
# remove temp files
rm -f "$STACK_DIR"/locals.tf
rm -f "$STACK_DIR"/provider.tf
rm -f "$STACK_DIR"/versions.tf

echo "Completed terraform $ACTION for stack $STACK for account type $ACCOUNT_TYPE and project $ACCOUNT_PROJECT"
