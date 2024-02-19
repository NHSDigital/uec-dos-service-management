#!/bin/bash

export BUILD_COMMIT_MESSAGE="$1"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    echo $BUILD_COMMIT_MESSAGE is valid
else :
    echo $BUILD_COMMIT_MESSAGE is not valid
fi
