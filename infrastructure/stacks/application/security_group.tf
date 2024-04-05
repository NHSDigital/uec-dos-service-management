module "application_lambda_security_group" {
  source = "../../modules/security-group"

  vpc_name             = "${var.project}-${var.vpc_name}-${var.environment}"
  name                 = var.application_lambda_security_group_name
  description          = "Security group for application lambda"
  apply_default_egress = true
}

# Add ingress to the aurora SG from this SG
resource "aws_vpc_security_group_ingress_rule" "application_lambda_ingress" {
  security_group_id = data.aws_security_group.aurora_security_group.id

  referenced_security_group_id = module.application_lambda_security_group.id
  from_port                    = 5432
  ip_protocol                  = "tcp"
  to_port                      = 5432

  description = "A rule to allow incomming connections from the Lambda Application SG"
}
