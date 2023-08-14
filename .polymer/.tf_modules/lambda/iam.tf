data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "role" {
  name               = var.lambda_role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "policy" {
  count = contains(keys(local.decoded_envfile), "iam_permissions") ? 1 : 0
  dynamic "statement" {
    for_each = local.decoded_envfile.iam_permissions

    content {
      sid       = statement.key
      effect    = statement.value["effect"]
      actions   = statement.value["actions"]
      resources = statement.value["resources"]
    }
  }
}

resource "aws_iam_policy" "policy" {
  count       = contains(keys(local.decoded_envfile), "iam_permissions") ? 1 : 0
  name        = format("CustomPolicyFor%s", var.lambda_function_name)
  description = "Custom policy managed with Terraform"
  policy      = data.aws_iam_policy_document.policy[0].json
}

locals {
  iam_policies = merge(
    {
      "LambdaBasicExecution" : "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    },
    contains(keys(local.decoded_envfile), "iam_permissions") ? {
      "AdditionalPolicies" : aws_iam_policy.policy[0].arn
    } : {}
  )
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role = aws_iam_role.role.name

  depends_on = [
    aws_iam_policy.policy[0]
  ]

  for_each = local.iam_policies

  policy_arn = each.value
}
