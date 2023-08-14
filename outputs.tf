output "function_name" {
  value = {
    for key, fn in module.lambda :
    key => fn.function_name
  }
}

output "api_gateway_integration_urls" {
  value = {
    for key, api in module.api :
    key => api.api_gateway_integration_url
  }
}
