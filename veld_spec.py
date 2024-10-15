import jsonschema

SCHEMA_DICT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "about": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "null"
                },
                "topics": {
                    "type": "null"
                }
            },
            "additionalProperties": False
        }
    },
    "oneOf": [
        {
            "type": "object",
            "properties": {
                "x-veld": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "oneOf": [
                                {
                                    "$ref": "#/definitions/about"
                                },
                                {
                                    "type": "null"
                                }
                            ]
                        }
                    },
                    "required": [
                        "data"
                    ],
                    "additionalProperties": False
                }
            },
            "required": [
                "x-veld"
            ],
            "additionalProperties": False
        },
        {
            "type": "object",
            "properties": {
                "x-veld": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "oneOf": [
                                        {
                                            "$ref": "#/definitions/about"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ]
                                }
                            },
                            "required": [
                                "code"
                            ],
                            "additionalProperties": False
                        },
                        {
                            "type": "object",
                            "properties": {
                                "chain": {
                                    "oneOf": [
                                        {
                                            "$ref": "#/definitions/about"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ]
                                }
                            },
                            "required": [
                                "chain"
                            ],
                            "additionalProperties": False
                        }
                    ]
                },
                "services": {
                    "type": "null"
                }
            },
            "required": [
                "x-veld",
                "services"
            ],
            "additionalProperties": False
        }
    ]
}


def validate(veld_metadata):
    try:
        jsonschema.validate(instance=veld_metadata, schema=SCHEMA_DICT)
        print("valid.")
    except jsonschema.exceptions.ValidationError as err:
        print("invalid")
        raise err


if __name__ == "__main__":
    validate()
