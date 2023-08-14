provider "aws" {
  shared_credentials_files = [".aws/credentials"]
  region                   = var.aws_region
  profile                  = "default"
}

locals {
  general_config       = yamldecode(file(format("${path.root}/%s", var.infrastructure_config_filename)))
  application_name     = local.general_config.application_name
  dynamodb_config      = lookup(local.general_config, "dynamodb", {})
  lambda_config        = lookup(local.general_config, "lambda", {})
  api_config           = lookup(local.general_config, "api_lambda_integration", {})
  lambda_function_name = format("%sfunction-%s", local.application_name, var.application_stage)
}


module "dynamodb" {
  count           = length(local.dynamodb_config) != 0 ? 1 : 0
  source          = "./.polymer/.tf_modules/dynamodb"
  dynamodb_config = local.dynamodb_config
}


module "lambda" {
  for_each             = local.lambda_config
  source               = "./.polymer/.tf_modules/lambda"
  application_name     = local.application_name
  application_stage    = var.application_stage
  lambda_function_name = format(each.value.function_name, var.application_stage)
  lambda_alias_name    = upper(var.application_stage)
  lambda_role_name     = format("${each.value.function_name}-role", var.application_stage)
  basedir              = format("${path.root}/%s", each.value.basedir)
  envfile_basedir      = format("${path.root}/%s", each.value.envfile_basedir)
}

module "codedeploy" {
  for_each             = local.lambda_config
  source               = "./.polymer/.tf_modules/codedeploy"
  deployapp_name       = format("%s%s-deploy", local.application_name, var.application_stage)
  deploygroup_name     = format("%s%s-deploygroup", local.application_name, var.application_stage)
  lambda_function_name = module.lambda[each.key].function_name
  lambda_version       = module.lambda[each.key].version
  lambda_alias_name    = upper(var.application_stage)
  lambda_alias_version = module.lambda[each.key].alias_version
  deployment_config    = lookup(each.value, "deployment_config", "CodeDeployDefault.LambdaAllAtOnce")
  aws_region           = var.aws_region
}

module "api" {
  for_each             = local.api_config
  source               = "./.polymer/.tf_modules/api"
  api_gateway_name     = format("%s%s-api", local.application_name, var.application_stage)
  lambda_function_name = module.lambda[each.key].function_name
  lambda_alias_name    = upper(var.application_stage)
  application_stage    = var.application_stage
  lambda_alias_arn     = module.lambda[each.key].alias_arn
  cors_handler_name    = lookup(each.value, "cors_handler_name", "")
  cors_configuration   = contains(keys(each.value), "cors_configuration") ? [each.value.cors_configuration] : []
}
