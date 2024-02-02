module "org-data-load" {
  source = "../../modules/lambda"

  function_name = "org_data_load"
  description   = "To pull ODS organizations data and write to DynamoDB table"
  handler       = "org_data_load.lambda_handler"
  layers = [
    "arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python39:14",
    "arn:aws:lambda:${var.aws_region}:${local.account_id}:layer:requests:1"
  ]

  environment_variables = {
    "ODS_CODES_XLSX_FILE" : "ODS_Codes.xlsx",
    "S3_DATA_BUCKET" : var.sm_datasource_bucket_name
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
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/organisation_affiliations${local.workspace_suffix}",
                      "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/organisations${local.workspace_suffix}"
                    ]
                },
                {
                    "Sid": "S3",
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket",
                        "s3:*Object"
                    ],
                    "Resource": [
                        "arn:aws:s3:${var.aws_region}:${local.account_id}:nhse-uec-sm-dev-databucket",
                        "arn:aws:s3:${var.aws_region}:${local.account_id}:nhse-uec-sm-dev-databucket/ODS_Codes.xlsx"
                    ]
                }
            ]
        }
        EOT
  ]
}
