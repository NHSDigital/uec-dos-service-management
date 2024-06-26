module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name           = "${var.function_name}${local.workspace_suffix}"
  handler                 = var.handler
  runtime                 = var.runtime
  publish                 = var.publish
  create_package          = var.create_package
  local_existing_package  = var.local_existing_package
  ignore_source_code_hash = var.ignore_source_code_hash
  attach_policy_jsons     = var.attach_policy_jsons
  number_of_policy_jsons  = var.number_of_policy_jsons
  description             = var.description
  policy_jsons            = var.policy_jsons
  timeout                 = var.timeout
  vpc_security_group_ids  = var.vpc_security_group_ids
  tracing_mode            = "Active"
  attach_tracing_policy   = true

  vpc_subnet_ids        = [for s in data.aws_subnet.private_subnet : s.id]
  attach_network_policy = true

  environment_variables = merge(var.environment_variables, { WORKSPACE = "${local.environment_workspace}", LOG_LEVEL = "${var.log_level}" })
  layers                = concat(local.common_layers, var.layers)
}

