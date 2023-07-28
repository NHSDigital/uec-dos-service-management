#!/bin/bash


all_pass=0
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR-1 My message takes exactly 72 characters to describe this new commit"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi
export BRANCH_NAME=main
export BUILD_COMMIT_MESSAGE="DR-1 My message takes exactly 72 characters to describe this new commit"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# invalid - jira project ref
export BRANCH_NAME=task/D-22_My_invalid_branch
export BUILD_COMMIT_MESSAGE="DR-1 My valid commit message"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
  all_pass=1
fi
# invalid - jira project ref
export BRANCH_NAME=task/DR2_My_invalid_branch
export BUILD_COMMIT_MESSAGE="DR-1 My valid commit message"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - no initial cap
export BRANCH_NAME=task/DR-2_my_invalid_branch
export BUILD_COMMIT_MESSAGE="DR-1 My valid commit message"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - jira ref too long
export BRANCH_NAME=task/DPTS-221111_My_invalid_br
export BUILD_COMMIT_MESSAGE="DR-1 My valid commit message"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - branch name too long
export BRANCH_NAME=task/DPTS-22111_My_invalid_branch
export BUILD_COMMIT_MESSAGE="DR-1 My valid commit message"
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

# invalid comment - no jira ref
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="My invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh  "My valid commit message"
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - incomplete jira ref
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="D-1 Invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -jira ref has no hyphen
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR1 Invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -jira ref too long
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR-111111 invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -no initial cap
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR-11 invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -no space after JIRA ref
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR-11My invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - min three words
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR-11 My message"
/bin/bash ./scripts/githooks/git-commit-msg.sh  "DR-11 My message"
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - too long
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export BUILD_COMMIT_MESSAGE="DR-11 My message takes too many characters to describe the commit clearly"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

if [ $all_pass = 1 ] ; then
  echo one or more tests failed
else
  echo all tests passed
fi

exit $all_pass
