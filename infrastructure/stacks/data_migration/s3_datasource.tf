module "sm_datasource_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${var.sm_datasource_bucket_prefix}-${var.environment}-${var.sm_datasource_bucket_name}${local.workspace_suffix}"
}
