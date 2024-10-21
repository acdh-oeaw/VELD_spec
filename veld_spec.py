from dataclasses import dataclass
from typing import List, Union

import yaml


@dataclass
class Node:
    pass


@dataclass
class Node:
    is_optional: bool = False
    is_variable: bool = False
    content: Union[str, None] = None
    
    def __repr__(self):
        return "Node: " + str(self.content)

    
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
    possibilities: List[Node] = None
    
    
@dataclass
class NodeVariableDefinition(Node):
    content: Union[Node, None] = None
    target: Union[Node, None] = None


def read_schema():
    
    def parse_data_block(data_block):
        global i
        global line_counter
        global node_container_level_dict
        global indentation_level_previous
        i = 0
        line_counter = 0
        node_container_level_dict = {0: None}
        indentation_level_previous = 0
        
        def state_symbol():
            global i
            symbol = ""
            optional_local_start = False
            optional_local_end = False
            while True:
                char = data_block[i]
                if char == "[":
                    optional_local_start = True
                elif char == "]":
                    optional_local_end = True
                elif char == "<":
                    pass
                elif char == ">":
                    pass
                elif char == "{":
                    pass
                elif char == "}":
                    pass
                elif char in [":", " ", "\n"]:
                    symbol_is_optional = optional_local_start and optional_local_end
                    outer_is_optional_start = optional_local_start and not optional_local_end
                    node = Node(content=symbol, is_optional=symbol_is_optional)
                    return [node, outer_is_optional_start]
                else:
                    symbol += char
                i += 1
        
        def state_target():
            global i
            is_optional = None
            node_list = []
            node_disjunction = None
            node_mapping = None
            while True:
                char = data_block[i]
                if char == " ":
                    i += 1
                elif char == "|":
                    if node_disjunction is not None:
                        node_disjunction = NodeDisjunction()
                        node_disjunction.is_optional = is_optional
                elif char == ":":
                    node_mapping = NodeMapping()
                    node_disjunction.is_optional = is_optional
                elif char == "\n":
                    if node_disjunction is not None:
                        node_disjunction.possibilities = node_list
                        return node_disjunction
                    elif node_mapping is not None:
                        node_mapping.content = node_list[0]
                        node_mapping.target = node_list[1]
                        return node_mapping
                    elif len(node_list) == 1:
                        return node_list[0]
                    else:
                        return None
                else:
                    node, is_optional = state_symbol()
                    node_list.append(node)
        
        def state_mapping():
            node_mapping = NodeMapping()
            content = state_target()
            if content is not None:
                node_mapping.target = content
            else:
                node_mapping.target = state_line_beginning()
            return node_mapping
        
        def state_var_definition():
            node_variable_definition = NodeVariableDefinition()
            content = state_target()
            if content is not None:
                node_variable_definition.target = content
            else:
                node_variable_definition.target = state_line_beginning()
            return node_variable_definition
        
        def state_line_beginning():
            global i
            global line_counter
            global indentation_level_previous
            line_counter += 1
            indentation_level = 0
            while True:
                if i == len(data_block):
                    return None
                char = data_block[i]
                if char == "\n":
                    i += 1
                elif char == " ":
                    indentation_level += 1
                    i += 1
                else:
                    node_parent = node_container_level_dict.get(indentation_level)
                    if node_parent is None or (indentation_level > indentation_level_previous):
                        node_parent = NodeDict(content=[])
                        node_container_level_dict[indentation_level] = node_parent
                    indentation_level_previous = indentation_level
                    key_node, is_optional = state_symbol()
                    char = data_block[i]
                    if char == ":":
                        i += 1
                        node_mapping = state_mapping()
                        node_mapping.content = key_node
                        node_mapping.is_optional = is_optional
                        node_parent.content.append(node_mapping)
                        state_line_beginning()
                        return node_parent
                    elif data_block[i:i + 3] == "::=":
                        i += 3
                        node_var = state_var_definition()
                        return node_var
        
        return state_line_beginning()
    
    def read_schema_main():
        with open("./README.md", "r") as f:
            data_block_header = ""
            data_block = ""
            is_data_block = False
            is_example = False
            root_node_disjunction = NodeDisjunction(possibilities=[])
            for line_n, line in enumerate(f, start=1):
                if line.startswith("##"):
                    data_block_header = line.replace("#", "").replace("\n", "").strip()
                    is_example = False
                elif line == "example:\n":
                    is_example = True
                elif line == "```\n":
                    if is_data_block and data_block_header != "" and not is_example:
                        try:
                            node = parse_data_block(data_block)
                        except Exception as ex:
                            pass
                        else:
                            root_node_disjunction.possibilities.append(node)
                        data_block_header = ""
                        data_block = ""
                        is_example = False
                    is_data_block = not is_data_block
                elif is_data_block and data_block_header != "":
                    data_block += line
            return root_node_disjunction
    
    return read_schema_main()


def validate(dict_to_validate: dict = None, yaml_to_validate: str = None):

    def validate_dict(obj_to_validate, node: Node, path=""):
        
        def handle_node_disjunction(obj_to_validate, node: NodeDisjunction, path):
            result_list = []
            is_one_valid = False
            for possible_node in node.possibilities:
                result_list.append(validate_dict(obj_to_validate, possible_node, path))
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
                    result = validate_dict(obj_value, target, path_sub)
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
                    result = validate_dict(obj_value, node.content, path + "/" + str(i))
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

    def validate_main():
        schema = read_schema()
        if dict_to_validate is not None:
            return validate_dict(dict_to_validate, schema)
        elif yaml_to_validate is not None:
            with open(yaml_to_validate, "r") as f:
                return validate_dict(yaml.safe_load(f), schema)
        else:
            raise Exception("no param passed")
            
    return validate_main()
