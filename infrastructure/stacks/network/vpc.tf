resource "aws_vpc" "main" {
  cidr_block = "10.${var.vpc_cidr_block_marker}.0.0/20"
  tags = {
    Name = "${var.project}-${var.vpc_name}-${var.environment}"
  }
}

resource "aws_subnet" "private_zone" {
  count             = length(data.aws_availability_zones.azs.names)
  vpc_id            = aws_vpc.main.id
  availability_zone = data.aws_availability_zones.azs.names[count.index]
  cidr_block        = "10.${var.vpc_cidr_block_marker}.${var.vpc_cidr_block_range_private[count.index]}.0/23"
}
