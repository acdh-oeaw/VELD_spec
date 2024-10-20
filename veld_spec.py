from dataclasses import dataclass
from typing import List, Union, Dict



@dataclass
class Node:
    is_optional: bool = False
    is_variable: bool = False
    content: Union[str, None] = None
    
@dataclass
class NodeMapping(Node):
    content: Union[Node, None] = None
    target: Union[Node, None] = None
    
@dataclass
class NodeDict(Node):
    content: List[NodeMapping] = None
    
@dataclass
class NodeList(Node):
    content: Node = None

@dataclass
class NodeDisjunction(Node):
    content: List[Node] = None


root = NodeDisjunction(
    content=[
        NodeDict(
            content=[
                NodeMapping(
                    content=Node(
                        content="x-veld"
                    ),
                    target=NodeDict(
                        content=[
                            NodeMapping(
                                content=Node(
                                    content="data"
                                ),
                                target=NodeDict(
                                    content=[
                                        NodeMapping(
                                            content=Node(
                                                content="description"
                                            ),
                                            target=Node(
                                                is_optional=True,
                                                content=None
                                            )
                                        ),
                                        NodeMapping(
                                            content=Node(
                                                content="topics"
                                            ),
                                            target=NodeDisjunction(
                                                is_optional=True,
                                                content=[
                                                    Node(
                                                        content=None
                                                    ),
                                                    NodeList(
                                                        content=Node(
                                                            content=None
                                                        ),
                                                    )
                                                ]
                                            )
                                        ),
                                        NodeMapping(
                                            is_optional=True,
                                            content=Node(
                                                content="additional"
                                            ),
                                            target=Node(
                                                is_optional=True,
                                                content=None
                                            )
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
            ]
        ),
        NodeDict(
            content=[
                NodeMapping(
                    content=Node(
                        content="x-veld"
                    ),
                    target=NodeDict(
                        content=[
                            NodeMapping(
                                content=Node(
                                    content="code"
                                ),
                                target=NodeDict(
                                    content=[
                                        NodeMapping(
                                            content=Node(
                                                content="description"
                                            ),
                                            target=Node(
                                                is_optional=True,
                                                is_variable=True,
                                                content=None
                                            )
                                        ),
                                        NodeMapping(
                                            content=Node(
                                                content="topics"
                                            ),
                                            target=NodeDisjunction(
                                                is_optional=True,
                                                content=[
                                                    Node(
                                                        content=None,
                                                        is_variable=True,
                                                    ),
                                                    NodeList(
                                                        content=Node(
                                                            content=None,
                                                            is_variable=True,
                                                        ),
                                                    )
                                                ]
                                            )
                                        ),
                                        NodeMapping(
                                            is_optional=True,
                                            content=Node(
                                                content="additional"
                                            ),
                                            target=Node(
                                                is_optional=True,
                                                is_variable=True,
                                                content="<ADDITIONAL>"
                                            )
                                        ),
                                    ]
                                )
                            )
                        ]
                    )
                ),
                NodeMapping(
                    content=Node(
                        content="services"
                    ),
                    target=NodeDict(
                        content=[
                            NodeMapping(
                                content=Node(
                                    content="<VELD_SERVICE_NAME>",
                                    is_variable=True,
                                ),
                                target=NodeDict(
                                    content=[
                                        NodeMapping(
                                            is_optional=True,
                                            content=Node(
                                                content="<DOCKER_COMPOSE_DEFINITION>",
                                                is_variable=True,
                                            ),
                                            target=Node(
                                                content="<DOCKER_COMPOSE_DEFINITION_TARGET>",
                                                is_variable=True,
                                            ),
                                        ),
                                        NodeMapping(
                                            content=Node(
                                                content="volumes"
                                            ),
                                            is_optional=True,
                                            target=NodeList(
                                                content=NodeDict(
                                                    content=[
                                                        NodeMapping(
                                                            content=Node(
                                                                content="<HOST_PATH>",
                                                                is_variable=True,
                                                            ),
                                                            target=Node(
                                                                content="<CONTAINER_PATH>",
                                                                is_variable=True,
                                                            )
                                                        )
                                                    ]
                                                ),
                                            ),
                                        ),
                                    ]
                                )
                            )
                        ]
                    )
                ),
            ]
        ),
    ]
)



def validate(obj_to_validate, node: Node, path=""):
    
    def handle_node_disjunction(obj_to_validate, node: NodeDisjunction, path):
        result_list = []
        is_one_valid = False
        for possible_node in node.content:
            result_list.append(validate(obj_to_validate, possible_node, path))
        for result in result_list:
            if result[0]:
                is_one_valid = True
        if not is_one_valid:
            all_errors = "; ".join(r[1] for r in result_list)
            return (False, f"all possible options are invalid: ({all_errors})")
        else:
            return (True, None)
    
    def handle_node_dict(obj_to_validate, node: NodeDict, path):
        
        def go_to_target(obj_value, target: Node, path):
            if obj_value is not None:
                result = validate(obj_value, target, path_sub)
                if not result[0]:
                    return result
            elif not target.is_optional:
                return (False, f"non-optional value missing at: {path_sub}/")
            return (True, None)
        
        if type(obj_to_validate) is not dict:
            return (False, f"is not dict at: {path}/")
        else:
            node_keys_variables = []
            for node_mapping in node.content:
                node_key = node_mapping.content.content
                node_target = node_mapping.target
                if node_mapping.content.is_variable:
                    node_keys_variables.append(node_mapping)
                    continue
                if node_key not in obj_to_validate and not node_mapping.is_optional:
                    return (False, f"non-optional key missing: '{node_key}', at: {path}/")
                else:
                    obj_value = obj_to_validate.pop(node_key, None)
                    path_sub = path + "/" + node_key
                    result = go_to_target(obj_value, node_target, path_sub)
                    if not result[0]:
                        return result
            for node_mapping in node_keys_variables:
                node_target = node_mapping.target
                obj_key = next(iter(obj_to_validate.keys()))
                obj_value = obj_to_validate.pop(obj_key)
                path_sub = path + "/" + obj_key
                result = go_to_target(obj_value, node_target, path_sub)
                if not result[0]:
                    return result
            if len(obj_to_validate) != 0:
                unmatched_keys = ",".join(k for k in obj_to_validate.keys())
                return (False, f"elements not matching anything at: {path + '/' + unmatched_keys}")
        return (True, None)
    
    def handle_node_mapping(obj_to_validate, node: NodeMapping, path):
        raise Exception
    
    def handle_node_list(obj_to_validate, node: NodeList, path):
        obj_type = type(obj_to_validate)
        if obj_type is not list:
            return (False, f"is not list, but {obj_type}, at: {path}/")
        else:
            for i, obj_value in enumerate(obj_to_validate):
                result = validate(obj_value, node.content, path + "/" + str(i))
                if not result[0]:
                    return result
        return (True, None)
    
    def handle_node(obj_to_validate, node: Node, path):
        obj_type = type(obj_to_validate)
        if obj_type in [dict, list]:
            return (False, f"is not primitive type, but {obj_type}, at: {path}/")
        elif obj_type is None and not node.is_optional:
            return (False, f"non-optional value is empty at: {path}/")
        # elif node.is_variable and not (node.content.startswith("<") and node.content.endswith(">")):
        #     return (False, f"node is variable, but has fixed content: {node.content},at {path}/")
        return (True, None)
    
    def validate_main(obj_to_validate, node: Node, path):
        if type(obj_to_validate) in [dict, list]:
            obj_to_validate = obj_to_validate.copy()
        if type(node) is NodeDisjunction:
            node: NodeDisjunction
            return handle_node_disjunction(obj_to_validate, node, path)
        elif type(node) is NodeDict:
            node: NodeDict
            return handle_node_dict(obj_to_validate, node, path)
        elif type(node) is NodeMapping:
            node: NodeMapping
            return handle_node_mapping(obj_to_validate, node, path)
        elif type(node) is NodeList:
            node: NodeList
            return handle_node_list(obj_to_validate, node, path)
        elif type(node) is Node:
            node: Node
            return handle_node(obj_to_validate, node, path)
    
    return validate_main(obj_to_validate, node, path)



test_dict_1 = {
    "x-veld": {
        "data": {
            "description": None
        }
    }
}

test_dict_2 = {
    "x-veld": {
        "data": {
            "description": None,
            "topics": "a",
        }
    }
}

test_dict_3 = {
    "x-veld": {
        "data": {
            "description": None,
            "topics": ["a", "b"],
        }
    }
}

test_dict_4 = {
    "x-veld": {
        "data": {
            "description": None,
            "topics": {"a": "b"},
        }
    }
}

test_dict_5 = {
    "x-veld": {
        "code": {
            "description": None,
            "topics": None,
        }
    },
    "services": {
        "veld": {
            "build": ".",
            "volumes": [
                {"host_path_1": "container_path_1"},
                {"host_path_2": "container_path_2"},
            ]
        }
    }
}


# print(validate(test_dict_1, root))
# print(validate(test_dict_2, root))
# print(validate(test_dict_3, root))
# print(validate(test_dict_4, root))
print(validate(test_dict_5, root))

pass


# def validate(veld_metadata):
#
#     def clean_str(data_block_str):
#         data_block_str_cleaned = ""
#         line = ""
#         for char in data_block_str:
#             if char in ["[", "]", "{", "}"]:
#                 char = "\\" + char
#             if char != "\n":
#                 line += char
#             else:
#                 if line != "" and ":" not in line:
#                     line += ":"
#                 line += "\n"
#                 data_block_str_cleaned += line
#                 line = ""
#         return data_block_str_cleaned
#
#     def clean_dict_recursively(data_block_dict):
#         data_block_dict_clean = {}
#         for k, v in data_block_dict.items():
#             k = k.replace("\\", "")
#             if type(v) is dict:
#                 v = clean_dict_recursively(v)
#             elif type(v) is str:
#                 v = v.replace("\\", "")
#             else:
#                 v = v
#             data_block_dict_clean[k] = v
#         return data_block_dict_clean
#
#     def parse_data_block(data_block_line_list):
#
#         def state_key(line):
#             key = ""
#             is_optional_counter = 0
#             for char_i, char in enumerate(line):
#                 if char == "[":
#                     is_optional_counter += 1
#                 elif char != ":" and char != " ":
#                     key += char
#                 else:
#                     pass
#
#
#
#         def state_start(line):
#             indentation_level = 0
#             for char_i, char in enumerate(line):
#                 if char == " ":
#                     indentation_level += 1
#                 else:
#                     state_key(line[char_i+1:])
#
#
#
#         data_block_dict = {}
#         for line_i, line in enumerate(data_block_line_list):
#             is_beginning = True
#             is_variable = False
#             is_key = True
#             is_optional_counter = 0
#             indentation_level = 0
#             key = ""
#             value = ""
#             for char in line:
#                 if is_beginning and char == " ":
#                     indentation_level += 1
#                 elif is_beginning and char != " ":
#                     is_beginning = False
#                 elif not is_beginning:
#                     if char == "[":
#                         is_optional_counter += 1
#                     elif char == "]":
#                         is_optional_counter -= 1
#                     elif char == "<":
#                         is_variable = True
#                     elif char == ">":
#                         is_variable = False
#                     elif is_key and char != ":" and char != " ":
#                         key += char
#                     elif is_key and char == ":":
#                         is_key = False
#                         is_value = True
#                     elif is_value and char != " ":
#                         value += char
#                     else:
#                         continue
#
#
#
#         return data_block_dict
#
#     def validate_main():
#         schema_dict = {}
#         with open("./README.md", "r") as f:
#             data_block_header = ""
#             data_block = ""
#             is_data_block = False
#             is_example = False
#             for line_n, line in enumerate(f, start=1):
#                 if line.startswith("##"):
#                     data_block_header = line.replace("#", "").replace("\n", "").strip()
#                     is_example = False
#                 elif line == "example:\n":
#                     is_example = True
#                 elif line == "```\n":
#                     if is_data_block and data_block_header != "" and not is_example:
#                         data_block_dict = {data_block_header: parse_data_block(data_block.split("\n"))}
#                         schema_dict.update(data_block_dict)
#                         data_block_header = ""
#                         data_block = ""
#                         is_example = False
#                     is_data_block = not is_data_block
#                 elif is_data_block and data_block_header != "":
#                     data_block += line
#
#         pass
#
#     return validate_main()
#
#
# if __name__ == "__main__":
#     validate({})
