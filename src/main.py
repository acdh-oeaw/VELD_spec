import json

import jsonschema


def validate(veld_metadata):
    with open("./veld_schema.json", "r") as schema_file:
        schema_dict = json.load(schema_file)
        try:
            jsonschema.validate(instance=veld_metadata, schema=schema_dict)
            print("valid.")
        except jsonschema.exceptions.ValidationError as err:
            print("invalid")
            raise err
    

if __name__ == "__main__":
    pass
