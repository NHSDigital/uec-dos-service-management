#!/bin/bash
#!/bin/bash
source ./scripts/functions/git-functions.sh

all_pass=0
# valid branch name at min length
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi
# main is a valid branch name
export BRANCH_NAME=main
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# valid branch name at max length
export BRANCH_NAME=task/DPTS-2_This_valid_branch_at_the_sixty_character_maximum
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
  all_pass=1
fi

# valid branch name with numbers
export BRANCH_NAME=task/DPTS-2211_My_route53_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# valid branch name with numbers
export BRANCH_NAME=task/DPTS-2211_Route53_new_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# valid branch name with numbers
export BRANCH_NAME=task/DPTS-2211_Route_new_branch99
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi


# tests for invalid branch names
# invalid - jira project ref

# branch name has special character ! at end
export BRANCH_NAME=task/DR-2_My_invalid_branch!
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

# branch name has special character £ at end
export BRANCH_NAME=task/DR-2211_My_valid_branch£
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

# branch name has special character £ in middle
export BRANCH_NAME=task/DR-2211_My_valid_£_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

# branch name has special character £ at start
export BRANCH_NAME=task/$DR-2211_My_valid_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

# invalid - jira project ref
export BRANCH_NAME=task/DR2_My_invalid_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - no initial cap
export BRANCH_NAME=task/DR-2_my_invalid_branch
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - jira ref too long
export BRANCH_NAME=task/DPTS-221111_My_invalid_br
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - branch name too long
export BRANCH_NAME=task/DPTS-2_This_invalid_branch_over_sixty_character_maximumq
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid - branch name too short
export BRANCH_NAME=DPTS-2_Invalid_name
/bin/bash ./scripts/githooks/git-branch-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

if [ $all_pass = 1 ] ; then
  echo one or more branch name tests failed
else
  echo all branch name tests passed
fi

# reset for commit message tests
all_pass=0

# valid commmit message test
export BUILD_COMMIT_MESSAGE="DR-1 My message takes exactly 101a characters to describe this commit as per agreed the maximum limit"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

#  number based tests
# # valid commmit message test with numbers
export BUILD_COMMIT_MESSAGE="DR-1 My message has 101 numbers"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# # valid commmit message test with numbers as second word
export BUILD_COMMIT_MESSAGE="DR-1 My 101 message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# # valid commmit message test with numbers as third word
export BUILD_COMMIT_MESSAGE="DR-1 My message 101"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# valid commmit message test with number in first word
export BUILD_COMMIT_MESSAGE="DR-1 Route53 record added"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# valid commmit message test with number in second word
export BUILD_COMMIT_MESSAGE="DR-1 Record route53 added"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# # number as part of third word
export BUILD_COMMIT_MESSAGE="DR-1 Record added route53"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi
# # number as part of word beyond first three
export BUILD_COMMIT_MESSAGE="DR-1 Record added for route53"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 1 ]]; then
    all_pass=1
fi

# invalid commit message tests

#  -- other tests

# invalid comment - includes a special character
# export BUILD_COMMIT_MESSAGE="£DR-1 My 101 message"
# /bin/bash ./scripts/githooks/git-commit-msg.sh
# if [[ $? = 0 ]]; then
#     all_pass=1
# fi
# # # invalid comment - includes a special character
# export BUILD_COMMIT_MESSAGE="DR-1 My #1 message"
# /bin/bash ./scripts/githooks/git-commit-msg.sh
# if [[ $? = 0 ]]; then
#     all_pass=1
# fi
# # # invalid comment - includes a special character
# export BUILD_COMMIT_MESSAGE="DR-1 My exclamation! message"
# /bin/bash ./scripts/githooks/git-commit-msg.sh
# if [[ $? = 0 ]]; then
#     all_pass=1
# fi

# # # invalid comment - includes a special character
# export BUILD_COMMIT_MESSAGE="TESTING-1 My valid message"
# /bin/bash ./scripts/githooks/git-commit-msg.sh
# if [[ $? = 0 ]]; then
#     all_pass=1
# fi

# # invalid comment - no jira ref
export BUILD_COMMIT_MESSAGE="My invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - incomplete jira ref
export BUILD_COMMIT_MESSAGE="D-1 Invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -jira ref has no hyphen
export BUILD_COMMIT_MESSAGE="DR1 Invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -jira ref too long
export BUILD_COMMIT_MESSAGE="DR-111111 invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -no initial cap
export BUILD_COMMIT_MESSAGE="DR-11 invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - initial number not cap
export BUILD_COMMIT_MESSAGE="DR-11 1nvalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment -no space after JIRA ref
export BUILD_COMMIT_MESSAGE="DR-11My invalid commit message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - min three words
export BUILD_COMMIT_MESSAGE="DR-11 My message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# invalid comment - too long
export BUILD_COMMIT_MESSAGE="DR-11 My message takes over the maximum of one hundred characters to describe the commit goal clearly"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

if [ $all_pass = 1 ] ; then
  echo one or more commit message tests failed
else
  echo all commit message tests passed
fi

all_pass=0
# test export_terraform_workspace_name
# DEPLOYMENT_WORKSPACE (if set used ; if not uses branch name)
# BRANCH_NAME (if not set = current branch name)
# unset both variables and reset as required before EACH test
# current branch - is used - this test will require work or simply enter expected result for current branch below

unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "dr-687" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from valid branch name
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "dpts-2211" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from main branch
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export BRANCH_NAME=main
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "default" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from deployment workspace
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export DEPLOYMENT_WORKSPACE=dr-665
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "dr-665" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from release workspace
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export DEPLOYMENT_WORKSPACE=R1.1.0
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "default" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from version workspace
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export DEPLOYMENT_WORKSPACE=V1.1.0
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "default" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from other workspace
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export DEPLOYMENT_WORKSPACE=other
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "other" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# workspace derived from empty workspace
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export DEPLOYMENT_WORKSPACE=""
export BRANCH_NAME=task/DPTS-2211_My_valid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME = "dpts-2211" ]]; then
    all_pass=0
else
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# invalid branch name
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export BRANCH_NAME=task/DPTS22_My_invalid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME != "" ]]; then
    all_pass=1
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from invalid branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# alternative invalid branch name
unset DEPLOYMENT_WORKSPACE
unset BRANCH_NAME
export BRANCH_NAME=task/DPTS-22_my_invalid_branch
export_terraform_workspace_name
if [[ $TERRAFORM_WORKSPACE_NAME != "" ]]; then
    all_pass=1
    echo "Wrong derived Workpace $TERRAFORM_WORKSPACE_NAME from invalid branch name $BRANCH_NAME and DEPLOYMENT_WORKSPACE $DEPLOYMENT_WORKSPACE"
fi

# summarise workspace test results
if [ $all_pass = 1 ] ; then
  echo one or more workspace tests failed
else
  echo all workspace tests passed
fi


exit $all_pass
