#! /bin/bash

# This script generates a requests lambda layer and uploads to target AWS account
set -e
# Before running this script:
#  - Login to an appropriate AWS account as appropriate user from commamnd-line
#  - Export the following variables prior to calling this script
#  -

# check required exports have been done
EXPORTS_SET=0
# # Check key variables have been exported - see above
# if [ -z "$USER_SHORTCODE" ] ; then
#   echo  USER_SHORTCODE not set
#   EXPORTS_SET=1
# fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi


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



