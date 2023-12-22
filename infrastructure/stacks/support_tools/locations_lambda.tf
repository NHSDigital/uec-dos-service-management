data "archive_file" "locations_lambda_deployment_file" {
  type        = "zip"
  source_dir  = "../../../scripts/locations_data_load"
  excludes    = ["../../../scripts/locations_data_load/locations_lambda.zip"]
  output_path = "../../../scripts/locations_data_load/locations_lambda.zip"
}

module "locations-lambda" {
  source = "../../modules/lambda"

  function_name = "locations_lambda"
  description   = "To pull ODS locations data nad write to DynamoDB Locations table"
  handler       = "locations_lambda.lambda_handler"

  local_existing_package = data.archive_file.locations_lambda_deployment_file.output_path

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
                        "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/data/api/lambda/client_secret"
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
                                "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/locations"
                            ]
                        }
                    ]
                }
            ]
        }
        EOT
  ]
}
