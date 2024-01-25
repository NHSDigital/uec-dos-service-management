locals {
  org_data_load_dir = "../../../scripts/org_data_load"
}


data "archive_file" "org_data_lambda_deployment_file" {
  type        = "zip"
  source_dir  = "${local.org_data_load_dir}/deploy"
  output_path = "${local.org_data_load_dir}/org_data_load_lambda.zip"
}


module "org-data-lambda" {
  source = "../../modules/lambda"

  function_name = "org_data_load_lambda"
  description   = "To pull ODS organizations data and write to DynamoDB table"
  handler       = "org_data_load.lambda_handler"
  layers = [
    "arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python39:14",
    "arn:aws:lambda:${var.aws_region}:${local.account_id}:layer:requests:1"
  ]
  local_existing_package = data.archive_file.org_data_lambda_deployment_file.output_path

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ListParameters",
                    "Effect": "Allow",
                    "Action": [
                        "ssm:DescribeParameters"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "UseParameters",
                    "Effect": "Allow",
                    "Action": [
                        "ssm:GetParameters"
                    ],
                    "Resource": [
                        "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/data/api/lambda/client_id",
                        "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/data/api/lambda/client_secret",
                        "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/data/api/lambda/ods/domain"
                    ]
                },
                {
                    "Sid": "AliasBasedKMS",
                    "Effect": "Allow",
                    "Action": [
                      "kms:Decrypt",
                      "kms:Encrypt",
                      "kms:GenerateDataKey*",
                      "kms:DescribeKey"
                    ],
                    "Resource": "arn:aws:kms:${var.aws_region}:${local.account_id}:key/*",
                    "Condition": {
                      "StringEquals": {
                        "kms:ResourceAliases": "alias/aws/ssm"
                      }
                    }
                },
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
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/organisation_affiliations",
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/organisations"
                    ]
                }
            ]
        }
        EOT
  ]
}
