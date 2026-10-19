resource "aws_vpc" "relief_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "relief-vpc-${var.environment}"
  }
}

resource "aws_internet_gateway" "relief_igw" {
  vpc_id = aws_vpc.relief_vpc.id

  tags = {
    Name = "relief-igw-${var.environment}"
  }
}

resource "aws_subnet" "relief_public_subnet" {
  vpc_id                  = aws_vpc.relief_vpc.id
  cidr_block              = var.subnet_cidr
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "relief-public-subnet-${var.environment}"
  }
}

resource "aws_route_table" "relief_public_rt" {
  vpc_id = aws_vpc.relief_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.relief_igw.id
  }

  tags = {
    Name = "relief-public-rt-${var.environment}"
  }
}

resource "aws_route_table_association" "relief_rta" {
  subnet_id      = aws_subnet.relief_public_subnet.id
  route_table_id = aws_route_table.relief_public_rt.id
}
