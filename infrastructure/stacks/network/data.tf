data "aws_region" "current" {}

data "aws_availability_zones" "azs" {
  state = "available"
}

data "aws_acm_certificate" "vpn_sm_server_cert" {
  domain      = "server"
  types       = ["IMPORTED"]
  statuses    = ["ISSUED"]
  most_recent = true
}
data "aws_acm_certificate" "vpn_sm_client_cert" {
  domain      = "client1.domain.tld"
  types       = ["IMPORTED"]
  statuses    = ["ISSUED"]
  most_recent = true
}

