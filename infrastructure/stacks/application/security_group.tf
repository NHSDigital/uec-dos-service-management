module "application_lambda_security_group" {
  source = "../../modules/security-group"

  vpc_name             = "${var.project}-${var.vpc_name}-${var.environment}"
  name                 = "application_lambda_sg"
  description          = "Security group for application lambda"
  apply_default_egress = true

}
