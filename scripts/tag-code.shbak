#! /bin/bash

# fail on first error
set -e
# This script generates a git tag
# The format for the tag is $TAG_TYPE-$TERRAFORM_WORKSPACE_NAME-$COMMIT_HASH_SHORT
# Where
# TAG_TYPE defaults to T but can we set by exporting an alternative value before calling script
# BRANCH_NAME =
# COMMIT_HASH_SHORT = short version of the commit hash (ie commit to be tagged)

# functions
source ./scripts/project-common.sh
source ./scripts/functions/terraform-functions.sh
source ./scripts/functions/git-functions.sh

# check exports have been done
EXPORTS_SET=0

if [ -z "$TAG_TYPE" ] ; then
    echo TAG_TYPE defaulting to test
    TAG_TYPE="test"
fi

if [ -z "$BRANCH_NAME" ] ; then
    echo BRANCH_NAME not set
    EXPORTS_SET=1
fi

export_terraform_workspace_name
export_short_commit_hash

if [ -z "$TERRAFORM_WORKSPACE_NAME" ] ; then
    echo TERRAFORM_WORKSPACE_NAME not derived
    EXPORTS_SET=1
fi
if [ -z "$COMMIT_HASH_SHORT" ] ; then
    echo COMMIT_HASH_SHORT not derived
    EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

# continue if required exports set
generate_tag



