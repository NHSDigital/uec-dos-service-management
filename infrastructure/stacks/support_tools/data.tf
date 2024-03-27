# "aws_vpc" "main"
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["${var.project}-${var.vpc_name}-${var.environment}"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "tag:Name"
    values = ["private_subnet"]
  }
}

data "aws_subnet" "private_subnet" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_security_group" "lambda_sg" {
  filter {
    name   = "tag:Name"
    values = ["lambda-sg"]
  }
}
