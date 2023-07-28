#!/bin/bash

GIT_BRANCH_PATTERN_PREFIX=task
GIT_BRANCH_PATTERN_SUFFIX='[A-Z]{2,5}-[0-9]{1,5}_[A-Z][a-z]+_[A-Za-z0-9]+_[A-Za-z0-9_]'
GIT_BRANCH_PATTERN=$GIT_BRANCH_PATTERN_PREFIX/$GIT_BRANCH_PATTERN_SUFFIX
GIT_BRANCH_MAX_LENGTH=32
GIT_COMMIT_MESSAGE_MAX_LENGTH=72
GIT_COMMIT_MESSAGE_PATTERN_MAIN='[A-Z]{2,5}-([0-9]{1,5})[[:space:]][A-Z][a-z]+[[:space:]][a-z]+[[:space:]][a-z]+'

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
    fi
}
function check_commit_message_length {
    BUILD_COMMIT_MESSAGE="$1"
    COMMIT_MESSAGE_LENGTH="$(echo $BUILD_COMMIT_MESSAGE | sed s/\'//g | head -1 | wc -m)"
    if [[ "$COMMIT_MESSAGE_LENGTH" -gt $GIT_COMMIT_MESSAGE_MAX_LENGTH ]] ; then
      echo At $COMMIT_MESSAGE_LENGTH characters the commit message exceeds limit of $GIT_COMMIT_MESSAGE_MAX_LENGTH
    fi
}


