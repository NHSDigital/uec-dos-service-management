resource "aws_security_group" "aurora_sg" {
  name        = "aurora-sg"
  description = "Security group for aurora"
  vpc_id      = data.aws_vpc.main.id
}

resource "aws_vpc_security_group_ingress_rule" "aurora_vpn_ingress" {
  security_group_id = aws_security_group.aurora_sg.id

  referenced_security_group_id = data.aws_security_group.vpn_secgroup.id
  from_port                    = 5432
  ip_protocol                  = data.aws_ec2_client_vpn_endpoint.service_management_vpn.transport_protocol
  to_port                      = 5432
}

resource "aws_vpc_security_group_ingress_rule" "aurora_application_lambda_ingress" {
  security_group_id = aws_security_group.aurora_sg.id

  referenced_security_group_id = data.aws_security_group.application_lambda_security_group.id
  from_port                    = 5432
  ip_protocol                  = "tcp"
  to_port                      = 5432

  description = "A rule to allow incomming connections from the Lambda Application SG"
}

resource "aws_vpc_security_group_ingress_rule" "aurora_data_migration_lambda_ingress" {
  security_group_id = aws_security_group.aurora_sg.id

  referenced_security_group_id = data.aws_security_group.data_migration_lambda_security_group.id
  from_port                    = 5432
  ip_protocol                  = "tcp"
  to_port                      = 5432

  description = "A rule to allow incomming connections from the Data Migration Lambda SG"
}
