#! /bin/bash

# This script generates a requests lambda layer and uploads to target AWS account
set -e
# Before running this script:
#  - Login to an appropriate AWS account as appropriate user from commamnd-line

echo Run pip install of requests package
mkdir python
cd python
pip install requests -t .
echo Create zip
zip -r requests_layer.zip .
echo Upload zip to AWS
aws lambda publish-layer-version --layer-name requests \
    --description "Requests layer" \
    --zip-file fileb://requests_layer.zip \
    --compatible-runtimes python3.9
echo Tidy up temp files
cd ..
rm -rf python



