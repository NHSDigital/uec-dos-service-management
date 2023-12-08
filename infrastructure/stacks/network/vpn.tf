# three routes one per subnet
resource "aws_ec2_client_vpn_route" "example" {
  count                  = length(data.aws_availability_zones.azs.names)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.service_management_vpn.id
  destination_cidr_block = "0.0.0.0/0"
  target_vpc_subnet_id   = aws_ec2_client_vpn_network_association.network_assoc_service_management[count.index].subnet_id
}
# three associations one per subnet
resource "aws_ec2_client_vpn_network_association" "network_assoc_service_management" {
  count                  = length(data.aws_availability_zones.azs.names)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.service_management_vpn.id
  subnet_id              = resource.aws_subnet.private_zone[count.index].id
}
# three authorization rules one per subnet
resource "aws_ec2_client_vpn_authorization_rule" "auth_rule_service_management_vpn" {
  count                  = length(data.aws_availability_zones.azs.names)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.service_management_vpn.id
  target_network_cidr    = resource.aws_subnet.private_zone[count.index].cidr_block
  authorize_all_groups   = true
}
# resource "aws_ec2_client_vpn_authorization_rule" "authorization_rule" {
#   client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.my_client_vpn.id

#   target_network_cidr    = "10.0.0.0/16"
#   authorize_all_groups   = true
# }

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
    Name = "vpn-sg"
  }
}

# one vpn
resource "aws_ec2_client_vpn_endpoint" "service_management_vpn" {
  description = "service-management-vpn"
  vpc_id      = resource.aws_vpc.main.id

  security_group_ids     = [aws_security_group.vpn_secgroup.id]
  split_tunnel           = true
  server_certificate_arn = aws_acm_certificate.server_vpn_cert.arn
  client_cidr_block      = "10.0.0.0/16"

  authentication_options {
    type                       = "certificate-authentication"
    root_certificate_chain_arn = aws_acm_certificate.client_vpn_cert.arn
  }

  connection_log_options {
    enabled               = true
    cloudwatch_log_group  = aws_cloudwatch_log_group.sm_log_group.name
    cloudwatch_log_stream = aws_cloudwatch_log_stream.sm_log_stream.name
  }
  # stuff that has to exist first
  depends_on = [
    aws_acm_certificate.server_vpn_cert,
    aws_acm_certificate.client_vpn_cert
  ]
}

resource "aws_cloudwatch_log_group" "sm_log_group" {
  name = "sm_vpn_log_group"
}

resource "aws_cloudwatch_log_stream" "sm_log_stream" {
  name           = "sm_vpn_log_stream"
  log_group_name = aws_cloudwatch_log_group.sm_log_group.name
}

resource "aws_acm_certificate" "server_vpn_cert" {
  certificate_body  = "TBA"
  private_key       = "TBA"
  certificate_chain = "TBA"
}

resource "aws_acm_certificate" "client_vpn_cert" {
  certificate_body  = "TBA"
  private_key       = "TBA"
  certificate_chain = "TBA"
}
