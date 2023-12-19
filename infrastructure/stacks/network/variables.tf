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

variable "log_group_retention_in_days" {
  description = "Number of days to retain logs generated by vpn"
  default     = 0
}

variable "recovery_window_in_days" {
  description = "Days before perm deletion"
  default     = 7
}

variable "vpn_tld_bucket_name" {
  description = "Name of bucket used to hold developer certs "
}
