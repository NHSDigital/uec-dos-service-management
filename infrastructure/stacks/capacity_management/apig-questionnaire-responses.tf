
resource "aws_api_gateway_resource" "questionnaire_responses_resource" {
  parent_id   = module.cm_rest_api.root_resource_id
  path_part   = "questionnaire_responses"
  rest_api_id = module.cm_rest_api.rest_api_id
}

resource "aws_api_gateway_method" "questionnaire_responses_get" {
  authorization = "NONE"
  http_method   = "GET"
  resource_id   = aws_api_gateway_resource.questionnaire_responses_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource
  ]
}

module "questionnaire_responses_integrations_get" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.questionnaire_responses_get.http_method
  lambda_function_name = var.questionnaire_responses_function_name
  gateway_resource_id  = aws_api_gateway_resource.questionnaire_responses_resource.id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource,
    aws_api_gateway_method.questionnaire_responses_get
  ]
}

resource "aws_api_gateway_method" "questionnaire_responses_put" {
  authorization = "NONE"
  http_method   = "PUT"
  resource_id   = aws_api_gateway_resource.questionnaire_responses_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource
  ]
}
module "questionnaire_responses_integrations_put" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.questionnaire_responses_put.http_method
  lambda_function_name = var.questionnaire_responses_function_name
  gateway_resource_id  = aws_api_gateway_resource.questionnaire_responses_resource.id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource,
    aws_api_gateway_method.questionnaire_responses_put
  ]
}

resource "aws_api_gateway_method" "questionnaire_responses_post" {
  authorization = "NONE"
  http_method   = "POST"
  resource_id   = aws_api_gateway_resource.questionnaire_responses_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource
  ]
}

module "questionnaire_responses_integrations_post" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.questionnaire_responses_post.http_method
  lambda_function_name = var.questionnaire_responses_function_name
  gateway_resource_id  = aws_api_gateway_resource.questionnaire_responses_resource.id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource,
    aws_api_gateway_method.questionnaire_responses_post
  ]
}

resource "aws_api_gateway_method" "questionnaire_responses_delete" {
  authorization = "NONE"
  http_method   = "DELETE"
  resource_id   = aws_api_gateway_resource.questionnaire_responses_resource.id
  rest_api_id   = module.cm_rest_api.rest_api_id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource
  ]
}

module "questionnaire_responses_integrations_delete" {
  source               = "../../modules/api-gateway-integrations"
  aws_region           = var.aws_region
  account_id           = local.account_id
  rest_api_id          = module.cm_rest_api.rest_api_id
  http_method          = aws_api_gateway_method.questionnaire_responses_delete.http_method
  lambda_function_name = var.questionnaire_responses_function_name
  gateway_resource_id  = aws_api_gateway_resource.questionnaire_responses_resource.id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource,
    aws_api_gateway_method.questionnaire_responses_delete
  ]
}

######
# Lambda permissions
######
module "questionnaire_responses_aws_lambda_permission" {
  source               = "../../modules/api-gateway-permissions"
  aws_region           = var.aws_region
  account_id           = local.account_id
  lambda_function_name = var.questionnaire_responses_function_name
  rest_api_id          = module.cm_rest_api.rest_api_id
}

#####
# CORS
#####
module "enable_cors_on_questionnaire_responses_resource_services" {
  source          = "squidfunk/api-gateway-enable-cors/aws"
  version         = "0.3.3"
  api_id          = module.cm_rest_api.rest_api_id
  api_resource_id = aws_api_gateway_resource.questionnaire_responses_resource.id

  depends_on = [
    aws_api_gateway_resource.questionnaire_responses_resource,
    module.cm_rest_api
  ]
}
