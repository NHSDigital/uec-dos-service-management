module "application_lambda_security_group" {
  source = "../../modules/security-group"

  depends_on = [
    aws_vpc.main
  ]

  vpc_name             = "${var.project}-${var.vpc_name}-${var.environment}"
  name                 = var.application_lambda_security_group_name
  description          = "Security group for application lambda"
  apply_default_egress = true
}

module "data_migration_lambda_security_group" {
  source = "../../modules/security-group"

  depends_on = [
    aws_vpc.main
  ]

  vpc_name             = "${var.project}-${var.vpc_name}-${var.environment}"
  name                 = var.data_migration_lambda_security_group_name
  description          = "Security group for data migration lambdas"
  apply_default_egress = true
}

