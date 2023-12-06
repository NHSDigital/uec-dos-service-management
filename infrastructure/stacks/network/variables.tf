variable "vpc_cidr_block_marker" {
  description = "CIDR block range marker to use with VPC"
}

variable "vpc_cidr_block_range_private" {
  description = "Third element to CIDR block range marker to use with VPC"
  type        = list(any)
  default     = [0, 2, 4]
}
variable "vpc_name" {
  description = "Name of vpc"
  type        = string
}
