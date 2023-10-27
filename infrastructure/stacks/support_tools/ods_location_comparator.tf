module "ods-location-comparator-lambda" {
  source = "../../modules/lambda"

  function_name = "ods-location-comparator"
  description   = "Lambda for checking ODS locations against DoS"

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
                        "s3:PutItem",
                        "s3:GetItem",
                        "s3:UpdateItem"
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
