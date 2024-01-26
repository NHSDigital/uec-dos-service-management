resource "aws_route53_zone" "private" {
  name = "${var.project}-mig-${var.environment}"
  vpc {
    vpc_id = aws_vpc.main.id
  }
}

resource "aws_route53_record" "dev" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "mig-datastore"
  type    = "CNAME"
  ttl     = 300
  records = ["aws_rds_cluster_instance"] #dummy endpoint until known#
}
