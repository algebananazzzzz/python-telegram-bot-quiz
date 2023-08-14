import yaml
import json
import copy


"""
Generates cleaned schema for use in application, based on provisioned dynamodb tables
"""


def app_dynamodb_config(config):
    crud_config = copy.deepcopy(config)

    def clean_index_schema(schema):
        schema.pop('read_capacity')
        schema.pop('write_capacity')
        schema.pop('projection_type', None)

        return schema

    for key in crud_config.keys():
        schema = crud_config[key]
        for index_type in ('global_secondary_index', 'local_secondary_index'):
            try:
                schema['indexes'] = {key: clean_index_schema(
                    value) for key, value in schema[index_type].items()}
                schema.pop(index_type)
            except KeyError:
                pass
        schema = clean_index_schema(schema)
        schema["table_name"] = f"{key}-{application_name}"

    return crud_config


def convert_dynamodb_type_to_graphql(dynamodb_type):
    if dynamodb_type == "S":
        return "String"
    elif dynamodb_type == "N":
        return "Float"
    elif dynamodb_type == "B":
        return "Boolean"
    elif dynamodb_type == "BOOL":
        return "Boolean"
    elif dynamodb_type == "NULL":
        return "Null"
    elif dynamodb_type == "M":
        return "JSON"
    elif dynamodb_type == "L":
        return "[JSON]"
    elif dynamodb_type == "SS":
        return "[String]"
    elif dynamodb_type == "NS":
        return "[Float]"
    elif dynamodb_type == "BS":
        return "[Boolean]"
    else:
        return "String"  # Default to String if type is unknown


def app_graphql_schema(schema):
    graphql_schema = ""

    for table_name, table_config in schema.items():
        attributes = table_config["attributes"]

        # Create object with field types
        field_types = {}
        for attr_name, attr_type in attributes.items():
            field_types[attr_name] = convert_dynamodb_type_to_graphql(
                attr_type)

        # Check if fields are used as hash key or sort key
        hash_key = table_config.get("hash_key")
        range_key = table_config.get("range_key")
        if hash_key:
            field_types[hash_key] = "ID!"
        if range_key:
            field_types[range_key] = "ID!"

        # Check global secondary indexes
        if "global_secondary_index" in table_config:
            for index_name, index_config in table_config["global_secondary_index"].items():
                index_hash_key = index_config.get("hash_key")
                index_range_key = index_config.get("range_key")
                if index_hash_key:
                    field_types[index_hash_key] = "ID!"
                if index_range_key:
                    field_types[index_range_key] = "ID!"

        # Generate GraphQL type
        graphql_schema += f"type {table_name.capitalize()} {{\n"
        for attr_name, attr_type in field_types.items():
            graphql_schema += f"    {attr_name}: {attr_type}\n"
        try:
            child = table_config["child"]
            graphql_schema += f"    {child}s: [{child.capitalize()}]\n"
        except KeyError:
            pass
        graphql_schema += "}\n\n"

    return graphql_schema


def dump_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file)


def dump_graphql_schema(filename, schema):
    with open(filename, "wt") as file:
        file.write(schema)


if __name__ == "__main__":
    with open(".polymer/infrastructure.yml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    application_name = config["application_name"]
    file_config = config["schema_files"]
    app_dynamodb = app_dynamodb_config(config["dynamodb"])
    app_graphql = app_graphql_schema(config["dynamodb"])

    dump_json(file_config["app_config_output"],
              {"application_name": application_name, "dynamodb": app_dynamodb})
    dump_graphql_schema(file_config["graphql_schema_output"], app_graphql)
