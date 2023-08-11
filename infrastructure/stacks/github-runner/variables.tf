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
variable "oidc_provider_url" {
  description = "Url of oidc provider"
}
variable "oidc_client" {
  description = "Client of oidc provider - eg aws"
}
variable "oidc_thumbprint" {
  description = "Thumbprint for oidc provider"
}
