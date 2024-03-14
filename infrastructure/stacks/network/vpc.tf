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
  tags = {
    Name = "private_subnet"
  }
}

resource "aws_subnet" "public_zone" {
  count             = length(data.aws_availability_zones.azs.names)
  vpc_id            = aws_vpc.main.id
  availability_zone = data.aws_availability_zones.azs.names[count.index]
  cidr_block        = "10.${var.vpc_cidr_block_marker}.${var.vpc_cidr_block_range_public[count.index]}.0/23"
  tags = {
    Name = "public_subnet"
  }
}

//creates internet gateway for outside connection with vpc
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "Internet Gateway"
  }
}

//creates route table with route to connect anywhere
resource "aws_route_table" "r" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "Route to internet"
  }
}

//associate route table with public subnet (all 3 in each az)
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public_zone)
  subnet_id      = aws_subnet.public_zone[count.index].id
  route_table_id = aws_route_table.r.id
}

//Create elastic IP for NAT Gateway
resource "aws_eip" "nat_eip" {
  domain = "vpc"

  tags = {
    Name = "EIP for NAT"
  }
}

//create nat gateway (nat per az required??
resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_zone[0].id
}

//creates route table for private subnet and NAT gateway
resource "aws_route_table" "r_nat" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "route table for private_nat"
  }
}

//associate route table with private subnet (all 3 in each az)
resource "aws_route_table_association" "nat_private" {
  count          = length(aws_subnet.public_zone)
  subnet_id      = aws_subnet.private_zone[count.index].id
  route_table_id = aws_route_table.r_nat.id
}
