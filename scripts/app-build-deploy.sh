#!/bin/bash

#THIS SCRIPT EXECUTES THE RELEVANT DEPLOYMENT ACTIONS FOR THIS MICROSERVICE.
#IT IS REFERENCED BY THE APPLICATION PIPELINE AND THEREFORE MUST ALWAYS BE CALLED "deploy_service.sh"

#INPUT ARGUMENTS
source ./scripts/functions/git-functions.sh

export SERVICE_NAME="${SERVICE_NAME:-""}"
echo "Service Name: ${SERVICE_NAME}"

export_terraform_workspace_name

SERVICE_NAME_WORKPACE="${SERVICE_NAME}-${TERRAFORM_WORKSPACE_NAME}"
echo "Service Name Workspace: ${SERVICE_NAME_WORKPACE}"

cd ./application/${SERVICE_NAME}

rsync -Rr ./ ./chalicebuildtmp
cd ./chalicebuildtmp
cp -r ../../../application-utils/* ./chalicelib/
pip install -r requirements.txt --target .

pip install chalice==1.29.0
chalice package ../chalicebuild

cd ../chalicebuild
LAMBDA_OUTPUT=$(aws lambda update-function-code --function-name=$SERVICE_NAME_WORKPACE --zip-file=fileb://deployment.zip --publish)
LATEST_VERSION=$(jq -r '.Version' --compact-output <<< "$LAMBDA_OUTPUT" )
PREVIOUS_VERSION=$(expr $LATEST_VERSION - 1)
echo "Latest version: ${LATEST_VERSION}"
echo "Previous version: ${PREVIOUS_VERSION}"
rm -r ../chalicebuildtmp

#PLEASE NOTE THAT FOR EXPEDIENCY, THE COMMANDS BELOW SIMPLY UPDATE THE FUNCTION CODE AND PUBLISH A NEW VERSION.
#IN FUTURE, IT WOULD BE MORE APPROPRIATE TO BUILD AN IMAGE OF THE SERVICE, NAME IT WITH THE COMMIT HASH
#AND PUSH THE IMAGE TO AN ARTIFACT REGISTRY, BEFORE DEPLOYING THAT ARTIFACT

# if [ $ENVIRONMENT_NAME = 'staging' ]
# #FOR CERTAIN ENVIRONMENTS, WE MAY WANT TO USE A CANARY STYLE DEPLOYMENT WHERE TRAFFIC IS SPLIT BETWEEN THE NEW VERSION AN THE PREVIOUS VERSTION
# then
#     ROUTING_CONFIG=\'{"AdditionalVersionWeights" : {'"$LATEST_VERSION"' : 0.05} }\'
#     aws lambda update-alias --function-name=$SERVICE_NAME --name live-service --function-version $PREVIOUS_VERSION --routing-config '{"AdditionalVersionWeights" : {$PREVIOUS_VERSION : 0.05} }'
# else
#     aws lambda update-alias --function-name=$SERVICE_NAME --name live-service --function-version $LATEST_VERSION  --routing-config '{}'
# fi           #
