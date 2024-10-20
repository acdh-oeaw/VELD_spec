from dataclasses import dataclass
from typing import List, Union, Dict


@dataclass
class Node:
    pass


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
class NodeVariableDefinition(Node):
    content: str = None
    possibilities: List[Node] = None


def validate(obj_to_validate, node: Node, path=""):
    
    def handle_node_disjunction(obj_to_validate, node: NodeVariableDefinition, path):
        result_list = []
        is_one_valid = False
        for possible_node in node.possibilities:
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
        if type(node) is NodeVariableDefinition:
            node: NodeVariableDefinition
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


def read_schema():
    
    def clean_str(data_block_str):
        data_block_str_cleaned = ""
        line = ""
        for char in data_block_str:
            if char in ["[", "]", "{", "}"]:
                char = "\\" + char
            if char != "\n":
                line += char
            else:
                if line != "" and ":" not in line:
                    line += ":"
                line += "\n"
                data_block_str_cleaned += line
                line = ""
        return data_block_str_cleaned
    
    def clean_dict_recursively(data_block_dict):
        data_block_dict_clean = {}
        for k, v in data_block_dict.items():
            k = k.replace("\\", "")
            if type(v) is dict:
                v = clean_dict_recursively(v)
            elif type(v) is str:
                v = v.replace("\\", "")
            else:
                v = v
            data_block_dict_clean[k] = v
        return data_block_dict_clean
    
    # def parse_data_block_STATES(data_block):
    #
    #     def get_parent(node, parent_level):
    #         if parent_level == 0:
    #             return node
    #         else:
    #             return get_parent(node.parent, parent_level - 1)
    #
    #     def state_char_optional(char):
    #         if char == "[":
    #             print("optional start")
    #             return 1
    #         elif char == "]":
    #             print("optional end")
    #             return -1
    #         else:
    #             return 0
    #
    #     def state_char_variable(char):
    #         if char == "<":
    #             print("variable start")
    #             return 1
    #         elif char == ">":
    #             print("variable end")
    #             return -1
    #         else:
    #             return 0
    #
    #     def state_char_list(char):
    #         if char == "{":
    #             print("variable start")
    #             return 1
    #         elif char == "}":
    #             print("variable end")
    #             return -1
    #         else:
    #             return 0
    #
    #     def state_mapping_target(node, indentation_level, line_current, line_next_list):
    #         for i in range(len(line_current)):
    #             char = line_current[i]
    #             if char == " ":
    #                 continue
    #             if char != "\n":
    #                 state_node(node, indentation_level, line_current[i+1:], line_next_list)
    #             else:
    #                 state_line_start(node, indentation_level, line_next_list)
    #
    #     def state_dict():
    #         pass
    #
    #     def state_list():
    #         pass
    #
    #     def state_variable_definition(node, line_current, line_next_list):
    #         for i in range(len(line_current)):
    #             char = line_current[i]
    #             if char == " ":
    #                 continue
    #             if char != "\n":
    #                 state_node(node, indentation_level, line_current[i+1:], line_next_list)
    #             else:
    #                 state_line_start(node, indentation_level, line_next_list)
    #
    #
    #     def state_node(node, indentation_level, line_current, line_next_list):
    #         symbol = ""
    #         node_is_optional = False
    #         node_is_variable = False
    #         node_can_be_optional = 0
    #         node_can_be_variable = 0
    #         node_can_be_list = 0
    #         for i in range(len(line_current)):
    #             char = line_current[i]
    #             counter_optional_change = state_char_optional(char)
    #             if counter_optional_change != 0:
    #                 if counter_optional_change == -1 and node_can_be_optional == 1:
    #                     node_is_optional = True
    #                 node_can_be_optional += counter_optional_change
    #                 continue
    #             counter_variable_change = state_char_variable(char)
    #             if counter_variable_change != 0:
    #                 if counter_variable_change == -1 and node_can_be_variable == 1:
    #                     node_is_variable = True
    #                 node_can_be_variable += counter_variable_change
    #                 continue
    #             counter_list_change = state_char_list(char)
    #             if counter_list_change != 0:
    #                 if counter_list_change == -1 and node_can_be_list == 1:
    #                     node_is_list = True
    #                 node_can_be_list += counter_list_change
    #                 continue
    #             if char not in [":", " ", "-", "\n"]:
    #                 symbol += char
    #             else:
    #                 if char == ":":
    #                     print("key")
    #                     node_mapping = NodeMapping(
    #                         content=Node(
    #                             content=symbol,
    #                             is_optional=node_is_optional,
    #                             is_variable=node_is_variable,
    #                         ),
    #                     )
    #                     node_mapping.target = state_mapping_target(None, indentation_level, line_current[i+1:], line_next_list)
    #                     if node is None:
    #                         node = NodeDict(content=[])
    #                     node.content.append(node_mapping)
    #                 elif line_current[i:i + 4] == " ::= ":
    #                     print("variable definition")
    #                     node = NodeVariableDefinition(
    #                         content=symbol,
    #                         is_optional=node_is_optional,
    #                         is_variable=node_is_variable,
    #                     )
    #                     i += 5
    #                     node = state_variable_definition(node, line_current[i:], line_next_list)
    #                 elif char == "-":
    #                     print("list")
    #                     if node is None:
    #                         node = NodeList()
    #                     node = state_list(None, line_current[i:], line_next_list)
    #                 elif char == "\n":
    #                     print("leaf")
    #                     node = Node(
    #                         content=symbol,
    #                         is_optional=node_is_optional,
    #                         is_variable=node_is_variable,
    #                     )
    #         return node
    #
    #     def state_line_start(node, indentation_level_above, line_next_list):
    #         line_current = line_next_list[0]
    #         line_next_list = line_next_list[1:]
    #         indentation_level_current = 0
    #         for i in range(len(line_current)):
    #             char = line_current[i]
    #             if char == " ":
    #                 indentation_level_current += 1
    #             else:
    #                 if indentation_level_current < indentation_level_above:
    #                     parent_level = (indentation_level_above - indentation_level_current) / 2
    #                     node_parent = get_parent(node, parent_level)
    #                     node = state_node(node_parent, indentation_level_current, line_current[i:], line_next_list)
    #                 elif indentation_level_current == indentation_level_above:
    #                     node = state_node(node, indentation_level_current, line_current[i:], line_next_list)
    #                 elif indentation_level_current > indentation_level_above:
    #                     node = state_node(None, indentation_level_current, line_current[i:], line_next_list)
    #         return node
    #
    #
    #     def parse_data_block_main():
    #         return state_line_start(None, 0, data_block.split("\n"))
    #
    #     parse_data_block_main()
        
    def parse_data_block(data_block):
        node_parent_for_level = {0: None}
        indentation_level_current = 0
        indentation_level_previous = 0
        current_optional_counter = 0
        state_optional_closed = False
        symboL_mapping_key_or_var_def = ""
        symbol_current = ""
        for line in data_block.splitlines(keepends=True):
            node_current = None
            state_beginning = True
            state_symbol = False
            state_first_symbol = False
            state_after_symbol_is_mapping_or_var_def = False
            state_after_symbol_is_mapping_target = False
            state_key_or_var_def = False
            state_mapping_key = False
            state_mapping_target = False
            state_var_def = False
            state_list = False
            state_optional_open = False
            for char_i, char in enumerate(line):
                if state_beginning:
                    if char == " ":
                        indentation_level_current += 1
                    else:
                        state_beginning = False
                        state_first_symbol = True
                        if (indentation_level_current - indentation_level_previous) == 2:
                            node_parent_for_level[indentation_level_current] = None
                elif state_first_symbol:
                    if char == "-":
                        state_list = True
                    else:
                        state_symbol = True
                        state_after_symbol_is_mapping_or_var_def = True
                    state_first_symbol = False
                elif state_symbol:
                    if char == " ":
                        continue
                    elif char == "[":
                        state_optional_open = True
                        current_optional_counter += 1
                    elif char == "]":
                        state_optional_closed = True
                        state_optional_open = False
                        current_optional_counter -= 1
                    elif char == "<":
                        pass
                    elif char == ">":
                        pass
                    elif char == "{":
                        pass
                    elif char == "}":
                        pass
                    else:
                        if state_after_symbol_is_mapping_or_var_def:
                            if char != ":":
                                symbol_current += char
                            else:
                                state_symbol = False
                                state_key_or_var_def = True
                                state_after_symbol_is_mapping_or_var_def = False
                                symboL_mapping_key_or_var_def = symbol_current
                                symbol_current = ""
                        elif state_after_symbol_is_mapping_target:
                            if char != "\n":
                                symbol_current += char
                            else:
                                if symbol_current != "":
                                    node_current.target = Node(content=symbol_current)
                                    state_after_symbol_is_mapping_target = False
                                    
                elif state_key_or_var_def:
                    if char in [":", "="]:
                        symbol_current += char
                    elif symbol_current == "::=":
                        state_var_def = True
                    else:
                        state_mapping_key = True
                        state_key_or_var_def = False
                        symbol_current = ""
                elif state_mapping_key:
                    node_parent = node_parent_for_level[indentation_level_current]
                    if node_parent is None:
                        node_parent = NodeDict(content=[])
                        node_parent_for_level[indentation_level_current] = node_parent
                    node_current = NodeMapping(
                        content=Node(
                            content=symboL_mapping_key_or_var_def,
                            is_optional=state_optional_closed,
                        ),
                        is_optional=state_optional_open,
                    )
                    node_parent.content.append(node_current)
                    state_symbol = True
                    state_after_symbol_is_mapping_target = True
                    symboL_mapping_key_or_var_def = ""
                elif state_var_def:
                    pass
                elif state_list:
                    pass
            node_previous = node_current
            
        
    
    with open("./README.md", "r") as f:
        data_block_header = ""
        data_block = ""
        is_data_block = False
        is_example = False
        for line_n, line in enumerate(f, start=1):
            if line.startswith("##"):
                data_block_header = line.replace("#", "").replace("\n", "").strip()
                is_example = False
            elif line == "example:\n":
                is_example = True
            elif line == "```\n":
                if is_data_block and data_block_header != "" and not is_example:
                    parse_data_block(data_block)
                    data_block_header = ""
                    data_block = ""
                    is_example = False
                is_data_block = not is_data_block
            elif is_data_block and data_block_header != "":
                data_block += line


schema_test = NodeVariableDefinition(
    possibilities=[
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
                                            target=NodeVariableDefinition(
                                                is_optional=True,
                                                possibilities=[
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
                                            target=NodeVariableDefinition(
                                                is_optional=True,
                                                possibilities=[
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

# print(validate(test_dict_1, schema_test))
# print(validate(test_dict_2, schema_test))
# print(validate(test_dict_3, schema_test))
# print(validate(test_dict_4, schema_test))
# print(validate(test_dict_5, schema_test))


if __name__ == "__main__":
    schema = read_schema()
    pass