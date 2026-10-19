variable "aws_region" {
  type        = string
  description = "AWS region for deployment (e.g. ap-south-1 or us-east-1)"
  default     = "ap-south-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "production"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the dedicated relief VPC"
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR block for the public subnet"
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance sizing"
  default     = "t3.micro"
}

variable "container_image" {
  type        = string
  description = "Container image URI for deployment"
  default     = "123456789012.dkr.ecr.ap-south-1.amazonaws.com/disaster-relief-allocator:latest"
}

variable "container_port" {
  type        = number
  description = "Application port inside the container"
  default     = 8000
}
