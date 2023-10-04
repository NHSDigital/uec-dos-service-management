module "cm_datasource_bucket" {
  source      = "../../modules/s3"
  bucket_name = var.cm_datasource_bucket_name
}
