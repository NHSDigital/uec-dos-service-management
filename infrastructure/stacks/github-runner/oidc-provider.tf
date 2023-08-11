# resource "aws_iam_openid_connect_provider" "github_provider" {
#   url = var.oidc_provider_url
#   client_id_list = [
#     var.oidc_client,
#   ]
#   thumbprint_list = [
#     var.oidc_thumbprint
#   ]
# }
