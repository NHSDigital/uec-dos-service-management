# ==============================================================================
# Context

locals {
  account_id       = data.aws_caller_identity.current.id
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"

}
