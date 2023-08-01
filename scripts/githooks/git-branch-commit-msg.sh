#!/bin/bash
source ./scripts/functions/git-functions.sh
set -e

exit_code=0
BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}

# check branch name and commit message
check_git_branch_name $BRANCH_NAME
echo $1
echo branch check
[ $? != 0 ] && exit_code=1 ||:
exit $exit_code
