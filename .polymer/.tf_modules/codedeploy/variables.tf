variable "deployapp_name" {
  type = string
}

variable "deploygroup_name" {
  type = string
}

variable "lambda_function_name" {
  type = string
}

variable "lambda_version" {
  type = string
}

variable "lambda_alias_name" {
  description = "alias of lambda which will be deployed by CodeDeploy"
  type        = string
}

variable "lambda_alias_version" {
  type = string
}

variable "deployment_config" {
  type = string
}

variable "aws_region" {
  type = string
}
