module "vpn_tld_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${var.vpn_tld_bucket_name}-${var.environment}"
}
