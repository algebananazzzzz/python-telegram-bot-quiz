locals {
  dynamodb_config = var.dynamodb_config
}

resource "aws_dynamodb_table" "element-dynamodb-table" {
  for_each       = local.dynamodb_config
  name           = each.value.table_name
  read_capacity  = each.value.read_capacity
  write_capacity = each.value.write_capacity
  hash_key       = each.value.hash_key
  range_key      = try(each.value.range_key, null)

  dynamic "attribute" {
    for_each = each.value.key_attributes
    content {
      name = attribute.key
      type = attribute.value
    }
  }

  dynamic "global_secondary_index" {
    for_each = lookup(each.value, "global_secondary_index", {})

    content {
      name               = global_secondary_index.key
      hash_key           = global_secondary_index.value["hash_key"]
      range_key          = try(global_secondary_index.value["range_key"], null)
      write_capacity     = global_secondary_index.value["write_capacity"]
      read_capacity      = global_secondary_index.value["read_capacity"]
      projection_type    = global_secondary_index.value["projection_type"]
      non_key_attributes = global_secondary_index.value["projection_type"] == "INCLUDE" ? global_secondary_index.value["non_key_attributes"] : null
    }
  }

  dynamic "local_secondary_index" {
    for_each = lookup(each.value, "local_secondary_index", {})
    content {
      name            = local_secondary_index.key
      range_key       = local_secondary_index.value["range_key"]
      projection_type = local_secondary_index.value["projection_type"]
    }
  }
}
