
# three associations - one per subnet
resource "aws_ec2_client_vpn_network_association" "network_assoc_service_management" {
  count                  = length(data.aws_availability_zones.azs.names)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.service_management_vpn.id
  subnet_id              = resource.aws_subnet.private_zone[count.index].id
}
# three authorization rules - one per subnet
resource "aws_ec2_client_vpn_authorization_rule" "auth_rule_service_management_vpn" {
  count                  = length(data.aws_availability_zones.azs.names)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.service_management_vpn.id
  target_network_cidr    = resource.aws_subnet.private_zone[count.index].cidr_block
  authorize_all_groups   = true
}


# one security group
resource "aws_security_group" "vpn_secgroup" {
  name        = "vpn-sg"
  description = "Allow inbound traffic from port 443, to the VPN"
  vpc_id      = resource.aws_vpc.main.id

  ingress {
    protocol         = "tcp"
    from_port        = 443
    to_port          = 443
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    protocol         = "-1"
    from_port        = 0
    to_port          = 0
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "vpn-sm-sg"
  }
}

# one vpn
resource "aws_ec2_client_vpn_endpoint" "service_management_vpn" {
  description = "service-management-vpn"
  vpc_id      = resource.aws_vpc.main.id

  security_group_ids     = [aws_security_group.vpn_secgroup.id]
  split_tunnel           = true
  server_certificate_arn = data.aws_acm_certificate.vpn_sm_server_cert.arn
  client_cidr_block      = "11.${var.vpc_cidr_block_marker}.0.0/22"


  authentication_options {
    type                       = "certificate-authentication"
    root_certificate_chain_arn = data.aws_acm_certificate.vpn_sm_server_cert.arn
  }

  connection_log_options {
    enabled               = true
    cloudwatch_log_group  = aws_cloudwatch_log_group.sm_log_group.name
    cloudwatch_log_stream = aws_cloudwatch_log_stream.sm_log_stream.name
  }
}

resource "aws_cloudwatch_log_group" "sm_log_group" {
  name              = "sm-vpn-log-group"
  retention_in_days = var.log_group_retention_in_days
}

resource "aws_cloudwatch_log_stream" "sm_log_stream" {
  name           = "sm-vpn-log-stream"
  log_group_name = aws_cloudwatch_log_group.sm_log_group.name
}

# secrets manager to hold ca cert
resource "aws_secretsmanager_secret" "cert_secret" {
  name                    = "${var.repo_name}/vpn_ca_cert"
  recovery_window_in_days = var.recovery_window_in_days
}

# secrets manager to hold private key
resource "aws_secretsmanager_secret" "pk_secret" {
  name                    = "${var.repo_name}/vpn_ca_pk"
  recovery_window_in_days = var.recovery_window_in_days
}
