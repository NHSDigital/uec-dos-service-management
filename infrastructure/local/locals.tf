# ==============================================================================
# Context

locals {
  terraform-git-repo = "uec-dos-service-management"
  account_id         = data.aws_caller_identity.current.id
}
