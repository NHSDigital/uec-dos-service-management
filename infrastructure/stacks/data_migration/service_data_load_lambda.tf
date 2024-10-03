module "service_data_load_lambda" {
  source = "../../modules/lambda"

  function_name = "service_data_load"
  description   = "To load healthcare service data"
  handler       = "service_data_load_lambda.lambda_handler"
  layers = [
    "arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python312:8",
    "arn:aws:lambda:${var.aws_region}:${local.account_id}:layer:requests:1"
  ]
  timeout = "900"

  environment_variables = {
    "ODS_CODES_XLSX_FILE" : "Filtered_odscodes.xlsx",
    "S3_DATA_BUCKET" : "${var.sm_datasource_bucket_prefix}-${var.environment}-${var.sm_datasource_bucket_name}"
  }

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
                        "ssm:GetParameter*"
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
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/locations${local.workspace_suffix}",
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/organisations${local.workspace_suffix}",
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/healthcare_services${local.workspace_suffix}"
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
