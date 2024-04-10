# ==============================================================================
# Outputs

output "id" {
  description = "The id of the security group."
  value       = aws_security_group.security_group.id
}

output "name" {
  description = "The name of the security group."
  value       = aws_security_group.security_group.name
}
