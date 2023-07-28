#!/bin/bash
source ./scripts/functions/git-functions.sh
set -e

# https://flake8.pycqa.org/en/6.0.0/

PYTHON_FLAKE_IMAGE=6.0.0@sha256:bab9cabdf9ac8bfccf9da9bc0733037d516cd8389545f8b944305f79b4219411
PRECOMMIT=${PRECOMMIT:-true}
CODE_DIR=${CODE_DIR:-.}
BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}

function main {
  if [[ $(git-check-if-commit-changed-directory $PRECOMMIT $BRANCH_NAME $CODE_DIR) ]] ; then
    cmd="--max-line-length 120 ."
    docker run \
      --volume=$PWD:/scan \
      --workdir=/scan \
      alpine/flake8:$PYTHON_FLAKE_IMAGE $cmd
  fi

}

main $*
