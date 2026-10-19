resource "aws_security_group" "relief_web_sg" {
  name        = "relief-web-sg-${var.environment}"
  description = "Hardened security group for Disaster Relief Web Platform"
  vpc_id      = aws_vpc.relief_vpc.id

  # Inbound HTTP (80)
  ingress {
    description = "Allow inbound HTTP for redirection and health probes"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound HTTPS (443)
  ingress {
    description = "Allow secure inbound HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound HTTPS (443) only for pulling images from ECR / external APIs
  egress {
    description = "Allow secure outbound HTTPS for ECR and OS updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound HTTP (80) for package mirror resolution
  egress {
    description = "Allow outbound HTTP for OS package updates"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "relief-web-sg-${var.environment}"
  }
}
