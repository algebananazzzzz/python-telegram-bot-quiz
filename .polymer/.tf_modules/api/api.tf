resource "aws_apigatewayv2_api" "api" {
  name          = var.api_gateway_name
  protocol_type = "HTTP"

  dynamic "cors_configuration" {
    for_each = var.cors_configuration

    content {
      allow_origins  = cors_configuration.value.allow_origins
      allow_methods  = cors_configuration.value.allow_methods
      allow_headers  = cors_configuration.value.allow_headers
      max_age        = cors_configuration.value.max_age
      expose_headers = cors_configuration.value.expose_headers
    }
  }
}

resource "aws_apigatewayv2_stage" "api" {
  api_id = aws_apigatewayv2_api.api.id

  name        = var.application_stage
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "api_integration" {
  api_id = aws_apigatewayv2_api.api.id

  integration_uri  = var.lambda_alias_arn
  integration_type = "AWS_PROXY"

  request_parameters = {
    "overwrite:header.Content-Type" = "application/json"
  }
}

resource "aws_apigatewayv2_route" "api_integration" {
  api_id = aws_apigatewayv2_api.api.id

  route_key = "ANY /api"
  target    = "integrations/${aws_apigatewayv2_integration.api_integration.id}"
}

data "aws_lambda_function" "cors_handler" {
  count         = (var.cors_handler_name == "") ? 0 : 1
  function_name = var.cors_handler_name
}

resource "aws_apigatewayv2_integration" "cors_integration" {
  count  = (var.cors_handler_name == "") ? 0 : 1
  api_id = aws_apigatewayv2_api.api.id

  integration_uri    = data.aws_lambda_function.cors_handler[0].arn
  integration_type   = "AWS_PROXY"
  integration_method = "OPTIONS"
}

resource "aws_apigatewayv2_route" "cors_integration" {
  count  = (var.cors_handler_name == "") ? 0 : 1
  api_id = aws_apigatewayv2_api.api.id

  route_key = "OPTIONS /api"
  target    = "integrations/${aws_apigatewayv2_integration.cors_integration[0].id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.api.name}"

  retention_in_days = 1
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  qualifier     = var.lambda_alias_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_cors_gw" {
  count         = (var.cors_handler_name == "") ? 0 : 1
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.cors_handler_name
  principal     = "apigateway.amazonaws.com"

  # lifecycle {
  #   replace_triggered_by = [
  #     data.aws_lambda_function.cors_handler
  #   ]
  # }

  source_arn = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
