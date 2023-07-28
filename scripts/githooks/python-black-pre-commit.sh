#!/bin/bash
source ./scripts/functions/git-functions.sh
set -e

# https://black.readthedocs.io/en/stable/

PYTHON_BLACK_IMAGE=23.3.0@sha256:b56d7c26a8a39f4aa5d4def443a3aacf5ef325a4cdd0087cf698299138baeb38
PRECOMMIT=${PRECOMMIT:-true}
CODE_DIR=${CODE_DIR:-.}
BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}

function main {
  if [[ $(git-check-if-commit-changed-directory $PRECOMMIT $BRANCH_NAME $CODE_DIR) ]] ; then
    cmd="black ."
    docker run \
      --volume=$PWD:/scan \
      --workdir=/scan \
      pyfound/black:$PYTHON_BLACK_IMAGE $cmd
  fi

}

main $*
