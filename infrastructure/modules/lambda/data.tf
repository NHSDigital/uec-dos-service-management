data "aws_vpc" "uec_sm_vpc" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}

data "aws_subnets" "private_subnets" {

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.uec_sm_vpc.id]
  }
  filter {
    name   = "tag:Name"
    values = ["private_subnet"]
  }
}

data "aws_subnet" "private_subnet" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}
