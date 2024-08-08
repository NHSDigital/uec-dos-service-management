variable "sm_datasource_bucket_name" {
  description = "Name of s3 bucket that holds sm excel data sheet"
  type        = string
  default     = "nhse-${var.project}-${var.environment}-databucket"
}
