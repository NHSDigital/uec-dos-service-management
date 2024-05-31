
# aws_iam_role_policy = an inline policy
# aws_iam_policy, that is a managed policy and can be re-used
# Get the policy by name
data "aws_iam_policy" "power_user_policy" {
  name = "PowerUserAccess"
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "attach_power_user" {
  role       = aws_iam_role.github_runner_role.name
  policy_arn = data.aws_iam_policy.power_user_policy.arn
}
resource "aws_iam_policy" "ro_policy_iam" {
  name        = "${var.repo_name}-github-runner-iam-services"
  description = "Read-only policies for key iam permissions required by github runner"

  policy = file("uec-github-runner-iam-services.json")
}

resource "aws_iam_role_policy_attachment" "attach_ro_iam" {
  role       = aws_iam_role.github_runner_role.name
  policy_arn = aws_iam_policy.ro_policy_iam.arn
}

resource "aws_iam_policy" "access_policy_s3" {
  name        = "${var.repo_name}-github-runner-s3-access"
  description = "Policies to access artefact bucket in mgmt account"
  policy      = <<-EOF
  {
    "Version":"2012-10-17",
    "Statement": [

        {
            "Action": "s3:*",
            "Effect": "Allow",
            "Resource": "*",
            "Sid": "VisualEditor5"
        },

        {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": [
              "${data.aws_s3_bucket.artefact_bucket.arn}",
              "${data.aws_s3_bucket.released-artefact_bucket.arn}"
            ]
        },
        {
            "Action": [
                "s3:GetObject",
                "s3:GetObjectTagging",
                "s3:DeleteObject",
                "s3:PutObject",
                "s3:PutObjectTagging"
            ],
            "Effect": "Allow",
            "Resource": [
              "${data.aws_s3_bucket.artefact_bucket.arn}",
              "${data.aws_s3_bucket.released-artefact_bucket.arn}"
            ]
        }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "attach_s3_access" {
  role       = aws_iam_role.github_runner_role.name
  policy_arn = aws_iam_policy.access_policy_s3.arn
}


resource "aws_iam_role" "github_runner_role" {
  name               = "${var.repo_name}-github-runner"
  assume_role_policy = <<-EOF
    {
      "Version":"2012-10-17",
      "Statement":[
        {
          "Effect":"Allow",
          "Principal":{
            "Federated":"arn:aws:iam::${local.account_id}:oidc-provider/token.actions.githubusercontent.com"
          },
          "Action":"sts:AssumeRoleWithWebIdentity",
          "Condition":{
            "ForAllValues:StringLike":{
                "token.actions.githubusercontent.com:sub":"repo:${var.github_org}/${var.repo_name}:*",
                "token.actions.githubusercontent.com:aud":"sts.amazonaws.com"
              }
          }
        }
      ]
    }
    EOF
}
