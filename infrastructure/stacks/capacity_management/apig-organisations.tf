resource "aws_api_gateway_resource" "organisations_resource" {
  parent_id   = module.cm_rest_api.root_resource_id
  path_part   = "organisations"
  rest_api_id = module.cm_rest_api.rest_api_id
}

resource "aws_api_gateway_method" "organisations_get" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.organisations_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.organisations_resource
  ]
}

module "organisations_integrations_get" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.organisations_get.http_method
  lambda_function_name = var.organisations_function_name
  gateway_resource_id  = aws_api_gateway_resource.organisations_resource.id

  depends_on = [
    aws_api_gateway_resource.organisations_resource,
    aws_api_gateway_method.organisations_get
  ]
}

resource "aws_api_gateway_method" "organisations_put" {
  authorization = "NONE"
  http_method   = "PUT"
  resource_id   = aws_api_gateway_resource.organisations_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.organisations_resource
  ]
}
module "organisations_integrations_put" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.organisations_put.http_method
  lambda_function_name = var.organisations_function_name
  gateway_resource_id  = aws_api_gateway_resource.organisations_resource.id

  depends_on = [
    aws_api_gateway_resource.organisations_resource,
    aws_api_gateway_method.organisations_put
  ]
}

resource "aws_api_gateway_method" "organisations_post" {
  authorization = "NONE"
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.organisations_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.organisations_resource
  ]
}

module "organisations_integrations_post" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.organisations_post.http_method
  lambda_function_name = var.organisations_function_name
  gateway_resource_id  = aws_api_gateway_resource.organisations_resource.id

  depends_on = [
    aws_api_gateway_resource.organisations_resource,
    aws_api_gateway_method.organisations_post
  ]
}

resource "aws_api_gateway_method" "organisations_delete" {
  authorization = "NONE"
  http_method   = "DELETE"
  resource_id   = aws_api_gateway_resource.organisations_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.organisations_resource
  ]
}

module "organisations_integrations_delete" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.organisations_delete.http_method
  lambda_function_name = var.organisations_function_name
  gateway_resource_id  = aws_api_gateway_resource.organisations_resource.id

  depends_on = [
    aws_api_gateway_resource.organisations_resource,
    aws_api_gateway_method.organisations_delete
  ]
}

######
# Lambda permissions
######
module "organisations_aws_lambda_permission" {
  source               = "../../modules/api-gateway-permissions"
  aws_region           = var.aws_region
  account_id           = local.account_id
  lambda_function_name = var.organisations_function_name
  rest_api_id          = module.cm_rest_api.rest_api_id
}

#####
# CORS
#####
module "enable_cors_on_organisations_resource_services" {
  source          = "squidfunk/api-gateway-enable-cors/aws"
  version         = "0.3.3"
  api_id          = module.cm_rest_api.rest_api_id
  api_resource_id = aws_api_gateway_resource.organisations_resource.id

  depends_on = [
    aws_api_gateway_resource.organisations_resource,
    module.cm_rest_api
  ]
}
