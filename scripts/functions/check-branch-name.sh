#!/bin/bash

export BRANCH_NAME=$1
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    echo $BRANCH_NAME is valid
else :
    echo $BRANCH_NAME is not valid
fi
