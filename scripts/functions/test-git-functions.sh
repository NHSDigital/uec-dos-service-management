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
export BUILD_COMMIT_MESSAGE="£DR-1 My 101 message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
# # invalid comment - includes a special character
export BUILD_COMMIT_MESSAGE="DR-1 My number #1 message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

# # invalid comment - includes a special character
export BUILD_COMMIT_MESSAGE="DR-1 My bang message !"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

export BUILD_COMMIT_MESSAGE="DR-1 My amp er & sand message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

export BUILD_COMMIT_MESSAGE="DR-1 My exclamation message!"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi
export BUILD_COMMIT_MESSAGE="DR-1 My exc!amation message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

export BUILD_COMMIT_MESSAGE="DR-1 My percentage message %"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

export BUILD_COMMIT_MESSAGE="DR-1 My perc%ntage message"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

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

# invalid comment - More than 5 u/c at start
export BUILD_COMMIT_MESSAGE="TESTe-11 My valid messsage"
/bin/bash ./scripts/githooks/git-commit-msg.sh
if [[ $? = 0 ]]; then
    all_pass=1
fi

if [ $all_pass = 1 ] ; then
  echo one or more commit message tests failed
else
  echo all commit message tests passed
fi

exit $all_pass
