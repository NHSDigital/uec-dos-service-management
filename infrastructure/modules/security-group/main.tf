resource "aws_security_group" "security_group" {
  name        = "${var.name}${local.workspace_suffix}"
  description = var.description
  vpc_id      = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "lambda_egress" {
  count = (var.apply_default_egress == true ? 1 : 0)

  security_group_id = aws_security_group.security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
