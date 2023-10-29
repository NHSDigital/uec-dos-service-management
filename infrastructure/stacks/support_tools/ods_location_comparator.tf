  data "archive_file" "lambda_deployment_file" {
  type        = "zip"
  source_file = "../../../scripts/ods_location_comparator/ods_location_comparator.py"
  output_path = "../../../scripts/ods_location_comparator/ods_location_comparator.zip"
}

module "ods-location-comparator-lambda" {
  source = "../../modules/lambda"

  function_name = "ods-location-comparator"
  description   = "Lambda for checking ODS locations against DoS"

  local_existing_package = data.archive_file.lambda_deployment_file.output_path

  environment_variables = {
    "BASE_URL" : "",
    "GP_LOCATION_JSON_FILE" : "gp_locations.json",
    "PHARMACY_LOCATION_JSON_FILE" : "pharmacy_locations.json",
    "S3_DATA_BUCKET" : "nhse-uec-dos-dev-databucket",
    "TOKEN" : ""
  }

  policy_jsons = [
    <<-EOT
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "S3",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutOject",
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "*"
                    ]
                }
            ]
        }
        EOT
  ]
}
