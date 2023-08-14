
variable "application_stage" {
  type    = string
  default = "dev"
}

variable "infrastructure_config_filename" {
  default = ".polymer/infrastructure.yml"
}

variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}
