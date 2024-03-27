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
