# ==============================================================================
# Mandatory variables

variable "vpc_name" { description = "The name of the VPC to spin the Lambda up in" }

variable "function_name" { description = "The function name of the lambda" }

variable "description" { description = "The description of the lambda" }

variable "policy_jsons" { description = "Policy for Lambda to write to DynamoDB" }

variable "vpc_security_group_ids" { description = "Security group for lambdas" }

# ==============================================================================
# Default variables

variable "handler" {
  default = "app.lambda_handler"
}
variable "runtime" {
  default = "python3.12"
}
variable "publish" {
  default = true
}
variable "create_package" {
  default = false
}
variable "local_existing_package" {
  default = "./misc/init.zip"
}
variable "ignore_source_code_hash" {
  default = true
}
variable "attach_policy_jsons" {
  default = true
}
variable "number_of_policy_jsons" {
  default = "1"
}

variable "environment_variables" {
  default = {}
}

variable "layers" {
  default = []
}

variable "timeout" {
  default = "3"
}

variable "log_level" {
  default = "info"
}
