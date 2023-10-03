module "cm_rest_api" {
  source = "../../modules/api-gateway-rest-api"

  rest_api_name = var.rest_api_name
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = module.cm_rest_api.rest_api_id
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_method.healthcare_services_get,
    aws_api_gateway_method.locations_get,
    aws_api_gateway_method.organisations_get,
    aws_api_gateway_method.organisation_affiliations_get,
    aws_api_gateway_method.questionnaires_get,
    aws_api_gateway_method.questionnaire_responses_get,
    aws_api_gateway_method.healthcare_services_post,
    aws_api_gateway_method.locations_post,
    aws_api_gateway_method.organisations_post,
    aws_api_gateway_method.organisation_affiliations_post,
    aws_api_gateway_method.questionnaires_post,
    aws_api_gateway_method.questionnaire_responses_post,
    aws_api_gateway_method.healthcare_services_put,
    aws_api_gateway_method.locations_put,
    aws_api_gateway_method.organisations_put,
    aws_api_gateway_method.organisation_affiliations_put,
    aws_api_gateway_method.questionnaires_put,
    aws_api_gateway_method.questionnaire_responses_put,
    aws_api_gateway_method.healthcare_services_delete,
    aws_api_gateway_method.locations_delete,
    aws_api_gateway_method.organisations_delete,
    aws_api_gateway_method.organisation_affiliations_delete,
    aws_api_gateway_method.questionnaires_delete,
    aws_api_gateway_method.questionnaire_responses_delete,
    module.healthcare_services_integrations_post,
    module.healthcare_services_integrations_put,
    module.healthcare_services_integrations_get,
    module.healthcare_services_integrations_delete,
    module.locations_integrations_post,
    module.locations_integrations_put,
    module.locations_integrations_get,
    module.locations_integrations_delete,
    module.organisations_integrations_post,
    module.organisations_integrations_put,
    module.organisations_integrations_get,
    module.organisations_integrations_delete,
    module.organisation_affiliations_integrations_post,
    module.organisation_affiliations_integrations_put,
    module.organisation_affiliations_integrations_get,
    module.organisation_affiliations_integrations_delete,
    module.questionnaires_integrations_post,
    module.questionnaires_integrations_put,
    module.questionnaires_integrations_get,
    module.questionnaires_integrations_delete,
    module.questionnaire_responses_integrations_post,
    module.questionnaire_responses_integrations_put,
    module.questionnaire_responses_integrations_get,
    module.questionnaire_responses_integrations_delete,
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      module.cm_rest_api
    ]))
  }
}

resource "aws_api_gateway_stage" "stage" {
  deployment_id = aws_api_gateway_deployment.deployment.id
  rest_api_id   = module.cm_rest_api.rest_api_id
  stage_name    = "default"
}
