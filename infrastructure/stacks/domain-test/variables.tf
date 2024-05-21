variable "s3_bucket_name" {
  description = "Name of s3 bucket that holds downloaded csv"
}
variable "force_destroy" {
  description = "Whether to forcefully destroy the bucket when it contains objects"
  type        = bool
  default     = true
}
