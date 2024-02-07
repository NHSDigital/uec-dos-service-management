# Variables used in every stack
variable "project" {
  description = "Project code typically reflects sub project of project owner eg nhse-uec-dos"
}
variable "project_owner" {
  description = "Project owner based on orgnaistion and department code eg nhse-uec"
}
variable "environment" {
  description = "The environment - dev, test, staging etc"
}
variable "repo_name" {
  description = "The name of git hub repository"
}

variable "vpc_cidr_block_marker" {
  description = "CIDR block range marker to use with VPC"
}

variable "vpc_name" {
  description = "Name of vpc"
  type        = string
}

variable "vpn_security_group_name" {
  description = "value"

}

variable "tag_version" {
  description = "Identifies the version of tagging policy in use and supports changing it over time and any automation around the version."
  type        = string
}

variable "service" {
  description = "Identifies the service or programme."
  type        = string
}

variable "cost_centre" {
  description = "Supports Consolidated Billing and attribution of cost to Programmes."
  type        = string
}

variable "data_classification" {
  description = "See Cloud Risk Model, to enable quick searching of data classifications"
  type        = string
}

variable "data_type" {
  description = "identify the data type, None / PCD / PII / Anonymised / UserAccount / Audit"
  type        = string
}

variable "project_type" {
  description = "identifying the purpose of the resources, PoC, Pilot, Production"
  type        = string
}

variable "public_facing" {
  description = "Whether this is public facing via the internet"
  type        = string
}

variable "service_category" {
  description = "Used to identify response priorities"
  type        = string
}

variable "on_off_pattern" {
  description = "Used to automatically turn on and off machines that are not in a production environment."
  type        = string
}
