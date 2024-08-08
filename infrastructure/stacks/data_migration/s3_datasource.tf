module "sm_datasource_bucket" {
  source      = "../../modules/s3"
  bucket_name = "nhse-${var.project}-${var.environment}-databucket${local.workspace_suffix}"
}
