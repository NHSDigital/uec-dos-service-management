#! /bin/bash

# This script generates a .opvn file to get dev team member onto service management vpn
# fail on first error
set -e
# Before running this bootstrapper script:
#  - Login to an appropriate AWS account as appropriate user from commamnd-line
#  - Export the following variables prior to calling this script
#  - They are NOT set in this script to avoid details being stored in repo
# USER_SHORTCODE
# OPTIONAL
#   - VPN_DOMAIN - will default to uec-dos-sm-vpn
#   - VPN_DESC will default to service-management-vpn - the description of the VPN
#   - TEMP_VPN_CERT_DIR - will default to sm-vpn-certs (at root)

# check required exports have been done
EXPORTS_SET=0
# Check key variables have been exported - see above
if [ -z "$USER_SHORTCODE" ] ; then
  echo  USER_SHORTCODE not set
  EXPORTS_SET=1
fi

if [ $EXPORTS_SET = 1 ] ; then
  echo One or more exports not set
  exit 1
fi

export VPN_DOMAIN="${VPN_DOMAIN:-"uec-dos-sm-vpn"}"
export TEMP_VPN_CERT_DIR="${TEMP_VPN_CERT_DIR:-"sm-vpn-certs"}"
export VPN_DESC="${VPN_DESC:-"service-management-vpn"}"

echo Creating cert and key for user "$USER_SHORTCODE" for VPN "$VPN_DESC"

if [ -n "$OPEN_VPN_ROOT" ]; then
  OPEN_VPN_PROJ_DIR=$OPEN_VPN_ROOT/easy-rsa/easyrsa3
else
  OPEN_VPN_PROJ_DIR=~/projects/open-vpn/easy-rsa/easyrsa3
fi

cd $OPEN_VPN_PROJ_DIR
# generates following filees in following sub directories
# pki/private/nosuch.uec-dos-sm-vpn.tld.key
# pki/issued/nosuch.uec-dos-sm-vpn.tld.crt
# pki/inline/nosuch.uec-dos-sm-vpn.tld.inline
# reqs/nosuch.uec-dos-sm-vpn.tld

echo create client cert and key using easyrsa
# automates entry of yes at prompt generated by command
cat << EOF | ./easyrsa build-client-full $USER_SHORTCODE.$VPN_DOMAIN.tld nopass
yes
EOF

# create temp dir if not already exists
mkdir -p ~/$TEMP_VPN_CERT_DIR
echo copy previously generated ca crt to dedicated directory $TEMP_VPN_CERT_DIR
cp pki/ca.crt ~/$TEMP_VPN_CERT_DIR
echo copy generate client cert/key to dedicated directory
cp pki/issued/$USER_SHORTCODE.$VPN_DOMAIN.tld.crt ~/$TEMP_VPN_CERT_DIR
cp pki/private/$USER_SHORTCODE.$VPN_DOMAIN.tld.key ~/$TEMP_VPN_CERT_DIR

cd ~/$TEMP_VPN_CERT_DIR
echo importing generated client key and cert into AWS ACM...
aws acm import-certificate --certificate fileb://$USER_SHORTCODE.$VPN_DOMAIN.tld.crt \
--private-key fileb://$USER_SHORTCODE.$VPN_DOMAIN.tld.key \
--certificate-chain fileb://ca.crt \
> /dev/null

echo looking up vpn endpoint by name and protocol
CVN_ENPOINT=$(aws ec2 describe-client-vpn-endpoints --filters Name="transport-protocol",Values="tcp" \
| jq -r --arg VPN_DESC "$VPN_DESC" '.[] | .[] | select(.Description == $VPN_DESC) | .ClientVpnEndpointId')

echo generating draft opvn file for $USER_SHORTCODE for vpn endpoint $CVN_ENPOINT
aws ec2 export-client-vpn-client-configuration --client-vpn-endpoint-id $CVN_ENPOINT --output text>vpn_sm_config_$USER_SHORTCODE_temp.ovpn

echo get cert part of client crt file
cert=$(sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' $USER_SHORTCODE.$VPN_DOMAIN.tld.crt)

private_key=PRIVATE
echo get key element part of client key file
key=$(sed -n "/-----BEGIN $private_key KEY-----/,/-----END $private_key KEY-----/p" $USER_SHORTCODE.$VPN_DOMAIN.tld.key)

echo set insert marker for cert block into vpn_sm_config_$USER_SHORTCODE.ovpn
sed -i "s#</ca>#</ca>\n<cert>\nINSERT_CERT_HERE\n</cert>#g" vpn_sm_config_$USER_SHORTCODE_temp.ovpn

echo set insert marker for key block into vpn_sm_config_$USER_SHORTCODE.ovpn
sed -i "s#</cert>#</cert>\n<key>\nINSERT_KEY_HERE\n</key>#g" vpn_sm_config_$USER_SHORTCODE_temp.ovpn

awk -v cert="$cert" -v key="$key" '{gsub(/INSERT_CERT_HERE/,cert);gsub(/INSERT_KEY_HERE/,key); print}' vpn_sm_config_$USER_SHORTCODE_temp.ovpn  > vpn_sm_config_$USER_SHORTCODE.ovpn
echo File ready
