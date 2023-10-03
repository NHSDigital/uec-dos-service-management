resource "aws_cloudwatch_log_group" "logs" {
  name              = "${var.cloudwatch_log_group_name}${local.workspace_suffix}"
  retention_in_days = var.logs_retention_days
}
