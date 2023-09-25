data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = var.basedir
  output_path = "${path.root}/upload/lambda.zip"
}

locals {
  envfile_source  = format("${var.envfile_basedir}/${var.application_stage}.env.json")
  decoded_envfile = jsondecode(file(local.envfile_source))
}

resource "aws_lambda_function" "lambda" {
  filename      = data.archive_file.lambda.output_path
  function_name = var.lambda_function_name
  role          = aws_iam_role.role.arn
  handler       = lookup(local.decoded_envfile, "handler", "lambda_function.lambda_handler")

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime     = lookup(local.decoded_envfile, "runtime", "python3.9")
  memory_size = lookup(local.decoded_envfile, "memory_size", 128)

  environment {
    variables = tomap(try(local.decoded_envfile.environment_variables, {}))
  }

  dynamic "vpc_config" {
    for_each = contains(keys(local.decoded_envfile), "vpc_config") ? [1] : []

    content {
      subnet_ids         = lookup(local.decoded_envfile.vpc_config, "subnet_ids", [])
      security_group_ids = lookup(local.decoded_envfile.vpc_config, "security_group_ids", [])
    }
  }

  timeout = lookup(local.decoded_envfile, "timeout", 29)
  publish = true

  layers = [for layer in data.aws_lambda_layer_version.lambda_layers : layer.arn]

}

resource "aws_lambda_alias" "lambda" {
  name             = var.lambda_alias_name
  function_name    = var.lambda_function_name
  function_version = "42"

  # To use CodeDeploy, ignore change of function_version
  lifecycle {
    ignore_changes = [function_version, routing_config]
  }

  depends_on = [
    aws_lambda_function.lambda
  ]
}

data "aws_lambda_layer_version" "lambda_layers" {
  count      = length(try(local.decoded_envfile.layers, []))
  layer_name = local.decoded_envfile.layers[count.index]
}

