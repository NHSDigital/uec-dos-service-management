# ==============================================================================
# Mandatory variables

variable "name" { description = "The name of the security group" }
variable "description" { description = "The description of the security group" }
variable "vpc_name" { description = "The name of the VPC to create the security group in" }

# ==============================================================================

variable "apply_default_egress" {
  description = "Option to apply default egress to anywhere for this security group"
  default = false
}
