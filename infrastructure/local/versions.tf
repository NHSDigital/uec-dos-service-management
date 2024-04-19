terraform {
  required_version = ">= 1.5.0, < 1.6.0"

  backend "local" {
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40.0, < 5.43.0"
    }
  }
}
