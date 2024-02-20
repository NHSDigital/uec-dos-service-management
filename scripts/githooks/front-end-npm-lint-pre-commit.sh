#!/bin/bash
FRONTEND_DIRECTORY=src/frontend
# Navigate to the frontend directory if it exists
if [ -d "$FRONTEND_DIRECTORY" ]; then
  cd "$FRONTEND_DIRECTORY"  || exit
  # Run the linter #
  npm run lint
else
  echo No code to check
fi

