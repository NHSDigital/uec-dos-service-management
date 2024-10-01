module "sm_datasource_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${var.sm_datasource_bucket_name}-${var.environment}${local.workspace_suffix}"
}
