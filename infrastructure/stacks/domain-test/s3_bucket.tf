module "s3_bucket" {
  source        = "../../modules/s3"
  bucket_name   = "${var.s3_bucket_name}-${var.environment}${local.workspace_suffix}"
  force_destroy = var.force_destroy
}
