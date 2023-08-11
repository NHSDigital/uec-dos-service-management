variable "project" {
  description = "Project code typically reflects sub project of project owner eg nhse-uec-dos"
}
variable "project_owner" {
  description = "Project owner based on orgnaistion and department code eg nhse-uec"
}
variable "environment" {
  description = "The environment - dev, test, staging etc"
}
variable "terraform_lock_table_name" {
  description = "Name of dynamodb table that holds terraformn state locks"
}
variable "terraform_state_bucket_name" {
  description = "Name of s3 bucket that holds terraform state"
}
