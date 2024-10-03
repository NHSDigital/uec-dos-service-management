module "questionnaire_response_populator_lambda" {
  source = "../../modules/lambda"

  function_name = "cm_questionnaire_response_populator"
  description   = "To load data to DynamoDB"
  handler       = "questionnaire_and_response_populator.lambda_handler"
  layers = [
    "arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python312:8",
    # "arn:aws:lambda:${var.aws_region}:${local.account_id}:layer:requests:1"
  ]
  timeout = "900"

  environment_variables = {
    "S3_DATA_BUCKET" : "${var.sm_datasource_bucket_prefix}-${var.environment}-${var.sm_datasource_bucket_name}"
  }

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
                        "dynamodb:GetItem",
                        "dynamodb:Scan",
                        "dynamodb:Query",
                        "dynamodb:UpdateItem"
                    ],
                    "Resource":[
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/questionnaire_responses${local.workspace_suffix}",
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/questionnaires${local.workspace_suffix}"
                    ]
                },
                {
                    "Sid": "ListObjectsInBucket",
                    "Effect": "Allow",
                    "Action": [
                      "s3:ListBucket",
                      "s3:GetObject"
                    ],
                    "Resource": ["*"]
                }
            ]
        }
        EOT
  ]
  vpc_name               = "${var.project}-${var.vpc_name}-${var.environment}"
  vpc_security_group_ids = [data.aws_security_group.data_migration_lambda_security_group.id]
}
