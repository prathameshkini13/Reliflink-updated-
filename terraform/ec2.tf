data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM Role for EC2 to pull images from Amazon ECR without embedded credentials
resource "aws_iam_role" "relief_ec2_role" {
  name = "relief-ec2-ecr-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.relief_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "relief_instance_profile" {
  name = "relief-instance-profile-${var.environment}"
  role = aws_iam_role.relief_ec2_role.name
}

resource "aws_instance" "relief_app_server" {
  ami                  = data.aws_ami.amazon_linux_2023.id
  instance_type        = var.instance_type
  subnet_id            = aws_subnet.relief_public_subnet.id
  vpc_security_group_ids = [aws_security_group.relief_web_sg.id]
  iam_instance_profile = aws_iam_instance_profile.relief_instance_profile.name

  # DevSecOps Hardening: Enforce IMDSv2 (prevention of SSRF credential theft)
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  # Encrypted EBS root volume with gp3
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    encrypted             = true
    delete_on_termination = true
  }

  user_data = <<-EOF
              #!/bin/bash
              set -euo pipefail
              dnf update -y
              dnf install -y docker aws-cli
              systemctl enable --now docker

              # Login to ECR and start the hardened container
              aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${split("/", var.container_image)[0]}
              docker pull ${var.container_image}

              # Run container with maximum security flags:
              # - non-root user
              # - drop all Linux capabilities
              # - read-only root filesystem with dedicated tmpfs
              # - no-new-privileges
              docker run -d \
                --name relief-platform \
                --restart always \
                -p 80:8000 \
                --read-only \
                --tmpfs /tmp:rw,noexec,nosuid,size=64m \
                --cap-drop ALL \
                --security-opt no-new-privileges \
                ${var.container_image}
              EOF

  tags = {
    Name = "relief-app-server-${var.environment}"
  }
}
