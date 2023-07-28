#!/bin/bash
source ./scripts/functions/git-functions.sh
set -e

TF_VERSION=1.4.6@sha256:1dd96bd77801daa3880ab4943c5cb9d55ad5af51b803dcf6152b8bf8901a0a82
PRECOMMIT=${PRECOMMIT:-true}
IAC_DIR=${IAC_DIR:-infrastructure}
BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}

function main {
  if [[ $(git-check-if-commit-changed-directory $PRECOMMIT $BRANCH_NAME $IAC_DIR) ]] ; then
    cmd="fmt -recursive $IAC_DIR"
    docker run \
      --volume=$PWD:/scan \
      --workdir=/scan \
      hashicorp/terraform:$TF_VERSION $cmd
  fi

}

main $*
