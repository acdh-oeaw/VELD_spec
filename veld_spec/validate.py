import json

import jsonschema


def main(veld_metadata):
    with open("./veld_schema.json", "r") as schema_file:
        schema_dict = json.load(schema_file)
        try:
            jsonschema.validate(instance=veld_metadata, schema=schema_dict)
            print("valid.")
        except jsonschema.exceptions.ValidationError as err:
            print("invalid")
            raise err
    

if __name__ == "__main__":
    main

def __call__():
    print(1)



class MyModule:
    def __call__(self):
        self.main()

    def main(self):
        print("Hello from the module!")

# Create an instance of MyModule that is callable
validate = MyModule()
