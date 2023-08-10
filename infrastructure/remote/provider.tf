variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

data "aws_caller_identity" "current" {}

provider "aws" {
  region = var.aws_region

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true

  skip_requesting_account_id = false

  default_tags {
    tags = {
      owner               = var.project_owner
      project             = var.project
      environment         = var.environment
      terraform-base-path = replace(path.cwd, "/^.*?(${local.terraform-git-repo}\\/)/", "$1")
    }
  }
}

