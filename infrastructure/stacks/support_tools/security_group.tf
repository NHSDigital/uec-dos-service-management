resource "aws_security_group" "support_tools_lambda_sg" {
  name        = "support-tools-lambda-sg"
  description = "Security group for support tools lambdas"
  vpc_id      = data.aws_vpc.main.id

  tags = {
    Name = "support-tools-lambda-sg"
  }
}

resource "aws_vpc_security_group_egress_rule" "lambda_egress" {
  security_group_id = aws_security_group.support_tools_lambda_sg.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 0
  ip_protocol = "-1"
  to_port     = 0
}
