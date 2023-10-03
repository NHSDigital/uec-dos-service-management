/**************************
//
//ORGANISATIONS DATA MANAGER LAMBDA
//
**************************/


module "organisations-data-manager-lambda" {
  source = "../../modules/lambda"

  function_name = var.organisations_function_name
  description   = "Microservice for interacting with organisations dynamodb table"

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DynamodbTable",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": [
                        "${module.dynamodb_organisations_table.dynamodb_table_arn}"
                    ]
                }
            ]
        }
        EOT
  ]
}

#    allowed_triggers = {
#        AllowExecutionFromAPIGateway = {
#        service    = "apigateway"
#        source_arn = "${aws_api_gateway_rest_api.DoS_REST.execution_arn}/*/*"
#        }
#    }
#    }

#    module "live-alias-organisations-data-manager" {
#    source = "terraform-aws-modules/lambda/aws//modules/alias"

#    name          = "live-service"
#    function_name = module.organisations-data-manager-lambda.lambda_function_name
#    refresh_alias = false
#    }

/**************************
//
//ORGANISATION AFFILIATION DATA MANAGER LAMBDA
//
**************************/
module "organisation-affiliation-data-manager-lambda" {
  source = "../../modules/lambda"

  function_name = var.organisation_affiliations_function_name
  description   = "Microservice for interacting with organisation affiliation dynamodb table"

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DynamodbTable",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": [
                        "${module.dynamodb_organisation_affiliations_table.dynamodb_table_arn}"
                    ]
                }
            ]
        }
        EOT
  ]
}

#    allowed_triggers = {
#        AllowExecutionFromAPIGateway = {
#        service    = "apigateway"
#        source_arn = "${aws_api_gateway_rest_api.DoS_REST.execution_arn}/*/*"
#        }
#    }
#    }

#    module "live-alias-organisation-affiliation-data-manager" {
#    source = "terraform-aws-modules/lambda/aws//modules/alias"

#    name          = "live-service"
#    function_name = module.organisation-affiliation-data-manager-lambda.lambda_function_name
#    refresh_alias = false
#    }

/**************************
//
//LOCATIONS DATA MANAGER LAMBDA
//
**************************/
module "locations-data-manager-lambda" {
  source = "../../modules/lambda"

  function_name = var.locations_function_name
  description   = "Microservice for interacting with locations dynamodb table"

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DynamodbTable",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": [
                        "${module.dynamodb_locations_table.dynamodb_table_arn}"
                    ]
                }
            ]
        }
        EOT
  ]
}

#    allowed_triggers = {
#        AllowExecutionFromAPIGateway = {
#        service    = "apigateway"
#        source_arn = "${aws_api_gateway_rest_api.DoS_REST.execution_arn}/*/*"
#        }
#    }
#    }

#    module "live-alias-locations-data-manager" {
#    source = "terraform-aws-modules/lambda/aws//modules/alias"

#    name          = "live-service"
#    function_name = module.locations-data-manager-lambda.lambda_function_name
#    refresh_alias = false
#    }

/**************************
//
//HEALTHCARE SERVICES DATA MANAGER LAMBDA
//
**************************/
module "healthcare-services-data-manager-lambda" {
  source = "../../modules/lambda"

  function_name = var.healthcare_services_function_name
  description   = "Microservice for interacting with healthcare services dynamodb table"

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DynamodbTable",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": [
                        "${module.dynamodb_healthcare_services_table.dynamodb_table_arn}"
                    ]
                }
            ]
        }
        EOT
  ]
}

#    allowed_triggers = {
#        AllowExecutionFromAPIGateway = {
#        service    = "apigateway"
#        source_arn = "${aws_api_gateway_rest_api.DoS_REST.execution_arn}/*/*"
#        }
#    }
#    }

#    module "live-alias-healthcare-services-data-manager" {
#    source = "terraform-aws-modules/lambda/aws//modules/alias"

#    name          = "live-service"
#    function_name = module.healthcare-services-data-manager-lambda.lambda_function_name
#    refresh_alias = false
#    }

/**************************
//
//QUESTIONNAIRE DATA MANAGER LAMBDA
//
**************************/
module "questionnaire-data-manager-lambda" {
  source = "../../modules/lambda"

  function_name = var.questionnaires_function_name
  description   = "Microservice for interacting with questionnaire dynamodb table"

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DynamodbTable",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": [
                        "${module.dynamodb_questionnaires_table.dynamodb_table_arn}"
                    ]
                }
            ]
        }
        EOT
  ]
}

#    allowed_triggers = {
#        AllowExecutionFromAPIGateway = {
#        service    = "apigateway"
#        source_arn = "${aws_api_gateway_rest_api.DoS_REST.execution_arn}/*/*"
#        }
#    }
#    }

#    module "live-alias-questionnaire-data-manager" {
#    source = "terraform-aws-modules/lambda/aws//modules/alias"

#    name          = "live-service"
#    function_name = module.questionnaire-data-manager-lambda.lambda_function_name
#    refresh_alias = false
#    }

/**************************
//
//QUESTIONNAIRE RESPONSE DATA MANAGER LAMBDA
//
**************************/
module "questionnaire-response-data-manager-lambda" {
  source = "../../modules/lambda"

  function_name = var.questionnaire_responses_function_name
  description   = "Microservice for interacting with questionnaire response dynamodb table"

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DynamodbTable",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource": [
                        "${module.dynamodb_questionnaire_responses_table.dynamodb_table_arn}"
                    ]
                }
            ]
        }
        EOT
  ]
}

#    allowed_triggers = {
#        AllowExecutionFromAPIGateway = {
#        service    = "apigateway"
#        source_arn = "${aws_api_gateway_rest_api.DoS_REST.execution_arn}/*/*"
#        }
#    }
#    }

#    module "live-alias-questionnaire-response-data-manager" {
#    source = "terraform-aws-modules/lambda/aws//modules/alias"

#    name          = "live-service"
#    function_name = module.questionnaire-response-data-manager-lambda.lambda_function_name
#    refresh_alias = false
#    }
