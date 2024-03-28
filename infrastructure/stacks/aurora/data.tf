# "aws_vpc" "main"
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["${var.project}-${var.vpc_name}-${var.environment}"]
  }
}

data "aws_ec2_client_vpn_endpoint" "service_management_vpn" {
  filter {
    name   = "transport-protocol"
    values = ["tcp"]
  }
}

data "aws_security_group" "vpn_secgroup" {
  name = var.vpn_security_group_name
}

data "aws_security_group" "application_lambda_sg" {
  name = var.application_lambda_security_group_name
}

data "aws_security_group" "support_tools_lambda_sg" {
  name = var.support_tools_lambda_security_group_name
}
