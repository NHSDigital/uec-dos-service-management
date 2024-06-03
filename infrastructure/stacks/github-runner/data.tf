data "aws_s3_bucket" "artefact_bucket" {
  bucket = "nhse-mgmt-uec-dos-service-management-artefacts"
}

data "aws_s3_bucket" "released-artefact_bucket" {
  bucket = "nhse-mgmt-uec-dos-service-management-artefacts-released"
}
