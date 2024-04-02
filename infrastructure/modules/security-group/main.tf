resource "aws_security_group" "security_group" {
  name        = "${var.name}${local.workspace_suffix}"
  description = var.description
  vpc_id      = data.aws_vpc.vpc.id
}

# TODO Check that this is an acceptable policy for all SGs
resource "aws_vpc_security_group_egress_rule" "lambda_egress" {
  count = var.apply_default_egress

  security_group_id = aws_security_group.security_group.id
  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
}
