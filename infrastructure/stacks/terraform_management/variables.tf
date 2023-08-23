variable "terraform_lock_table_name" {
  description = "Name of dynamodb table that holds terraformn state locks"
}
variable "terraform_state_bucket_name" {
  description = "Name of s3 bucket that holds terraform state"
}
