#! /bin/bash
echo "Trigger: $TRIGGER"
echo "Trigger action: $TRIGGER_ACTION"
echo "Trigger reference: $TRIGGER_REFERENCE"

WORKSPACE="Unknown"

# If we are dealing with a tagging action, then the workspace is the name of the tag
if [ "$TRIGGER" == "tag" ] ; then
  WORKSPACE="$TRIGGER_REFERENCE"
  export WORKSPACE
  echo "Workspace from tag: $WORKSPACE"
fi

# If we are dealing with a push action and the trigger is not a tag, we'll need to look at the branch name
# to derive the workspace
if [ "$TRIGGER_ACTION" == "push" ] ; then
  BRANCH_NAME="${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
  BRANCH_NAME=$(echo $BRANCH_NAME | sed 's/refs\/heads\/task/task/g')

  if [ "$BRANCH_NAME" == "main" ] ; then
    WORKSPACE="default"
    echo "Workspace from main: $WORKSPACE"
  else
    IFS='/' read -r -a name_array <<< "$BRANCH_NAME"
    IFS='_' read -r -a ref <<< "${name_array[1]}"
    WORKSPACE=$(echo "${ref[0]}" | tr "[:upper:]" "[:lower:]")
    echo "Workspace every: $WORKSPACE"
  fi
fi

# We will need some further logic here to derive the workspace upon branch deletion
# TBC
export WORKSPACE


