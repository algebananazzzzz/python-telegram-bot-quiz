output "api_gateway_integration_url" {
  description = "Url of live lambda integration"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/${var.application_stage}/api"
}
