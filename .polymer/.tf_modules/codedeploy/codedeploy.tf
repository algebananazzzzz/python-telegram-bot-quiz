# ----------------------------------------------------------
# CodeDeploy resources
# ----------------------------------------------------------

resource "aws_codedeploy_app" "deploy" {
  compute_platform = "Lambda"
  name             = var.deployapp_name
}

resource "aws_codedeploy_deployment_group" "deploy" {
  app_name               = var.deployapp_name
  deployment_group_name  = var.deploygroup_name
  service_role_arn       = aws_iam_role.codedeploy_deployment_group_role.arn
  deployment_config_name = var.deployment_config

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  depends_on = [
    aws_iam_role.codedeploy_deployment_group_role
  ]
}

# ----------------------------------------------------------
# Trigger of deployment
# ----------------------------------------------------------

resource "null_resource" "run_codedeploy" {
  triggers = {
    # Run codedeploy when lambda version is updated
    lambda_version = var.lambda_version
  }

  provisioner "local-exec" {
    # Only trigger deploy when lambda version is updated (=lambda version is not 1)
    command = "export $(sed '1d;' .aws/credentials | xargs) ; if [ ${var.lambda_version} -ne 1 ] ;then aws deploy create-deployment --region ${var.aws_region} --application-name ${aws_codedeploy_app.deploy.name} --deployment-group-name ${aws_codedeploy_deployment_group.deploy.deployment_group_name} --revision '{\"revisionType\":\"AppSpecContent\",\"appSpecContent\":{\"content\":\"{\\\"version\\\":0,\\\"Resources\\\":[{\\\"${var.lambda_function_name}\\\":{\\\"Type\\\":\\\"AWS::Lambda::Function\\\",\\\"Properties\\\":{\\\"Name\\\":\\\"${var.lambda_function_name}\\\",\\\"Alias\\\":\\\"${var.lambda_alias_name}\\\",\\\"CurrentVersion\\\":\\\"${var.lambda_alias_version}\\\",\\\"TargetVersion\\\":\\\"${var.lambda_version}\\\"}}}]}\"}}';fi"
  }

  depends_on = [
    aws_codedeploy_deployment_group.deploy
  ]
}
