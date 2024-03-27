# resource "aws_security_group" "lambda_sg" {
#   name        = "lambda-sg"
#   description = "Security group for lambda"
#   vpc_id      = data.aws_vpc.main.id

#   tags = {
#     Name = "lambda-sg"
#   }
# }

# resource "aws_vpc_security_group_egress_rule" "lambda_egress" {
#   security_group_id = aws_security_group.lambda_sg.id

#   cidr_ipv4   = "0.0.0.0/0"
#   from_port   = 0
#   ip_protocol = "-1"
#   to_port     = 0
# }
