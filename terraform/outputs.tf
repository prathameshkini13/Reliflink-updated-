output "vpc_id" {
  description = "ID of the dedicated relief VPC"
  value       = aws_vpc.relief_vpc.id
}

output "instance_id" {
  description = "EC2 Instance ID running the platform"
  value       = aws_instance.relief_app_server.id
}

output "public_ip" {
  description = "Public IPv4 address of the platform instance"
  value       = aws_instance.relief_app_server.public_ip
}

output "public_dns" {
  description = "Public DNS hostname of the platform instance"
  value       = aws_instance.relief_app_server.public_dns
}

output "app_url" {
  description = "Web access URL for the Disaster Relief Platform"
  value       = "http://${aws_instance.relief_app_server.public_ip}"
}

output "health_endpoint" {
  description = "Cloud liveness probe URL"
  value       = "http://${aws_instance.relief_app_server.public_ip}/health"
}
