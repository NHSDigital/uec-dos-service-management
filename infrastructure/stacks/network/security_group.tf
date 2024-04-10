module "application_lambda_security_group" {
  source = "../../modules/security-group"

  vpc_name             = "${var.project}-${var.vpc_name}-${var.environment}"
  name                 = var.application_lambda_security_group_name
  description          = "Security group for application lambda"
  apply_default_egress = true
}

module "support_tools_lambda_security_group" {
  source = "../../modules/security-group"

  vpc_name             = "${var.project}-${var.vpc_name}-${var.environment}"
  name                 = var.support_tools_lambda_security_group_name
  description          = "Security group for support tool lambdas"
  apply_default_egress = true
}


