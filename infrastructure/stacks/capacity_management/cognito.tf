resource "aws_cognito_user_pool" "cm-user-pool" {
  name = "${var.cognito_pool_name}${local.workspace_suffix}"
}
resource "aws_cognito_user_pool_client" "cm-user-pool_client" {
  name         = "${var.cognito_pool_name}-client${local.workspace_suffix}"
  user_pool_id = aws_cognito_user_pool.cm-user-pool.id
}
