#!/bin/bash

GIT_BRANCH_PATTERN_PREFIX=task
GIT_BRANCH_PATTERN_SUFFIX='[A-Z]{2,5}-[0-9]{1,5}_[A-Z][a-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9_]'
GIT_SPECIAL_CHARS='[\~`!@#$£%^&*()=+{}|]'
GIT_BRANCH_PATTERN=$GIT_BRANCH_PATTERN_PREFIX/$GIT_BRANCH_PATTERN_SUFFIX
GIT_BRANCH_MAX_LENGTH=60
GIT_COMMIT_MESSAGE_MAX_LENGTH=100
GIT_COMMIT_MESSAGE_PATTERN_MAIN='[A-Z]{2,5}-([0-9]{1,5})[[:space:]][A-Z][a-z0-9]+[[:space:]][a-z0-9]+[[:space:]][a-z0-9]+'
GIT_SPECIAL_CHARS_MESSAGE='[£!%&]'
function git-check-if-commit-changed-directory {
    PRECOMMIT=$1
    BUILD_BRANCH=$2
    DIR=$3
    if [ "$PRECOMMIT" == true ]; then
      compare_to=HEAD
    elif [ "$BUILD_BRANCH" != main ]; then
      compare_to=main
    else
      compare_to=HEAD^
    fi
    git diff --name-only --cached $compare_to --diff-filter=ACDMRT | grep --quiet "^$DIR" && echo true || echo false
}

function check_git_branch_name {
    VALID_FORMAT=$(check_git_branch_name_format $1)
    VALID_LENGTH=$(check_git_branch_name_length $1)
    if [[ ! -z "$VALID_LENGTH" || ! -z "$VALID_FORMAT" ]] ; then
      [[ ! -z "$VALID_FORMAT" ]] && echo $VALID_FORMAT
      [[ ! -z "$VALID_LENGTH" ]] && echo $VALID_LENGTH
      return 1
    fi
}

function check_git_branch_name_format {
    BUILD_BRANCH="$1"
    if [ $BUILD_BRANCH != 'main' ] && ! [[ $BUILD_BRANCH =~ $GIT_BRANCH_PATTERN ]]  ; then
      echo Branch $BUILD_BRANCH does not match the naming pattern
    else
      if [ $BUILD_BRANCH != 'main' ] &&  [[ $BUILD_BRANCH =~ $GIT_SPECIAL_CHARS ]]  ; then
        echo Branch $BUILD_BRANCH includes special characters
      fi
    fi
}

function check_git_branch_name_length {
    BUILD_BRANCH="$1"
    if [[ ${#BUILD_BRANCH} -gt "$GIT_BRANCH_MAX_LENGTH" ]]; then
      echo At ${#BUILD_BRANCH} characters the branch name $1 exceeds max length
    fi
}

function check_git_commit_message {
    VALID_FORMAT=$(check_commit_message_format "$1")
    VALID_LENGTH=$(check_commit_message_length "$1")
    if [[ ! -z "$VALID_LENGTH" || ! -z "$VALID_FORMAT" ]] ; then
      [[ ! -z "$VALID_FORMAT" ]] && echo $VALID_FORMAT
      [[ ! -z "$VALID_LENGTH" ]] && echo $VALID_LENGTH
      return 1
    fi
}

function check_commit_message_format {
    BUILD_COMMIT_MESSAGE="$1"
    if ! [[ "$$(echo '$BUILD_COMMIT_MESSAGE' | sed s/\'//g | head -1)" =~ $GIT_COMMIT_MESSAGE_PATTERN_MAIN ]] ; then
      echo The commit message $BUILD_COMMIT_MESSAGE does not conform to the required rules
    else
      if [[ "$$(echo '$BUILD_COMMIT_MESSAGE' | sed s/\'//g | head -1)" =~ $GIT_SPECIAL_CHARS_MESSAGE ]]  ; then
        echo The commit message $BUILD_COMMIT_MESSAGE includes special characters
      fi
    fi
}
function check_commit_message_length {
    BUILD_COMMIT_MESSAGE="$1"
    COMMIT_MESSAGE_LENGTH="$(echo $BUILD_COMMIT_MESSAGE | sed s/\'//g | head -1 | wc -m)"
    if [[ "$COMMIT_MESSAGE_LENGTH" -gt $GIT_COMMIT_MESSAGE_MAX_LENGTH ]] ; then
      echo At $COMMIT_MESSAGE_LENGTH characters the commit message exceeds limit of $GIT_COMMIT_MESSAGE_MAX_LENGTH
    fi
}

# exports string to use as terraform workspace
# equal to DEPLOYMENT_WORKSPACE if previously exported and not a R or V tag
# or derived from branch name
function export_terraform_workspace_name {
    TERRAFORM_WORKSPACE_NAME="default"
    if [ -n "$DEPLOYMENT_WORKSPACE" ] ; then
        if  ! [[ $DEPLOYMENT_WORKSPACE =~ ^[RV]{1} ]]; then
          TERRAFORM_WORKSPACE_NAME=$(echo "$DEPLOYMENT_WORKSPACE" | tr "." "-")
        fi
    else
      BRANCH_NAME="${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
      BRANCH_NAME=$(echo $BRANCH_NAME | sed 's/refs\/heads\/task/task/g')
      if [ "$BRANCH_NAME" != 'main' ] && [[ $BRANCH_NAME =~ $GIT_BRANCH_PATTERN ]]  ; then
        IFS='/' read -r -a name_array <<< "$BRANCH_NAME"
        IFS='_' read -r -a ref <<< "${name_array[1]}"
        TERRAFORM_WORKSPACE_NAME=$(echo "${ref[0]}" | tr "[:upper:]" "[:lower:]")
      fi
    fi

    export TERRAFORM_WORKSPACE_NAME
}

# generate tag based on jira ref (derived from branch name ) commit hash and tag type
function generate_tag {
    if [ -z "$TAG_TYPE" ] ; then
      TAG_TYPE="test"
    fi
    GENERATED_TAG="$TERRAFORM_WORKSPACE_NAME-$COMMIT_HASH_SHORT-$TAG_TYPE"
    echo "$GENERATED_TAG"
}


function export_short_commit_hash {
    COMMIT_HASH_SHORT="$(git rev-parse --short HEAD)"
    export COMMIT_HASH_SHORT
}
