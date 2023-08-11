module "dynamodb_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "3.3.0"

  name                = var.table_name
  hash_key            = var.hash_key
  autoscaling_enabled = var.autoscaling_enabled

  attributes = var.attributes

  server_side_encryption_enabled = true
}
