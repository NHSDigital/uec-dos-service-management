module "dynamodb_organisations_table" {
  source = "../../modules/dynamodb"

  table_name = var.organisations_dynamodb_table_name
}

module "dynamodb_organisation_affiliations_table" {
  source = "../../modules/dynamodb"

  table_name = var.organisation_affiliations_dynamodb_table_name
}

module "dynamodb_locations_table" {
  source = "../../modules/dynamodb"

  table_name = var.locations_dynamodb_table_name
}

module "dynamodb_healthcare_services_table" {
  source = "../../modules/dynamodb"

  table_name = var.healthcare_services_dynamodb_table_name
}

module "dynamodb_questionnaires_table" {
  source = "../../modules/dynamodb"

  table_name = var.questionnaires_dynamodb_table_name
}

module "dynamodb_questionnaire_responses_table" {
  source = "../../modules/dynamodb"

  table_name = var.questionnaire_responses_dynamodb_table_name
}
