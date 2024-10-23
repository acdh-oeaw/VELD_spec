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
        return str(self.content)

    
@dataclass(repr=False)
class NodeMapping(Node):
    content: Union[Node, None] = None
    target: Union[Node, None] = None
    
    
@dataclass(repr=False)
class NodeDict(Node):
    content: List[NodeMapping] = None
    
    
@dataclass(repr=False)
class NodeList(Node):
    content: Node = None


@dataclass(repr=False)
class NodeDisjunction(Node):
    # TODO: rename possiblities to content
    possibilities: List[Node] = None
    
    
@dataclass(repr=False)
class NodeVariableDefinition(Node):
    content: Union[Node, None] = None
    target: Union[Node, None] = None


def read_schema():
    
    def parse_data_block(data_block):
        
        class CharState:
            def __init__(self):
                self.i = 0
                self.data_block = data_block
                # self.char = self.data_block[self.i]
                self.indentation_level_previous = 0
                
            def __repr__(self):
                i_end = self.i + 10
                if i_end == len(self.data_block):
                    i_end = len(self.data_block) - 1
                return f"{self.i, self.data_block[self.i], self.data_block[self.i:i_end]}"
            
            @property
            def char(self):
                return self.data_block[self.i]
            
            def has_char(self):
                return self.i < len(self.data_block)
                
            def next(self):
                if self.i < len(self.data_block):
                    self.i += 1
            
        cs = CharState()
        
        def state_symbol():
            symbol = ""
            is_variable = False
            while cs.has_char():
                if cs.char == "<" or cs.char == ">":
                    is_variable = True
                elif cs.char in [":", "]", "}", " ", "\n"]:
                    node = Node(content=symbol, is_variable=is_variable)
                    return node
                else:
                    symbol += cs.char
                cs.next()
        
        def state_next():
            node = None
            list_open = False
            list_close = False
            optional_open = False
            optional_close = False
            while cs.has_char():
                if cs.char == " ":
                    pass
                elif cs.char == "[":
                    optional_open = True
                elif cs.char == "]":
                    optional_close = True
                elif cs.char == "{":
                    list_open = True
                elif cs.char == "}":
                    if list_open:
                        node = NodeList(content=node)
                    list_close = True
                elif cs.char == ":":
                    cs.next()
                    if cs.char == ":":
                        cs.next()
                        if cs.char == "=":
                            cs.next()
                            node = NodeVariableDefinition(content=node)
                            node_next = state_next()
                            if type(node_next) is NodeMapping:
                                node_next = NodeDict(content=[node_next])
                            node.target = node_next
                    else:
                        node = NodeMapping(content=node)
                        node.target = state_next()
                    continue
                elif cs.char == "|":
                    cs.next()
                    node = NodeDisjunction(possibilities=[node])
                    node_next = state_next()
                    if type(node_next) is NodeDisjunction:
                        for node_next_possible in node_next.possibilities:
                            node.possibilities.append(node_next_possible)
                    else:
                        node.possibilities.append(node_next)
                    continue
                elif cs.char == "\n":
                    return node
                else:
                    node = state_symbol()
                    continue
                cs.next()
            
        def state_line_beginning(indentation_level_previous):
            node = None
            indentation_level = 0
            while cs.has_char():
                if cs.char == "\n":
                    indentation_level = 0
                elif cs.char == " ":
                    indentation_level += 1
                else:
                    if indentation_level == indentation_level_previous:
                        node_line = state_next()
                        if type(node_line) is NodeMapping:
                            if node is None:
                                node = NodeDict(content=[])
                            node.content.append(node_line)
                        elif type(node_line) is NodeVariableDefinition:
                            node = node_line
                        continue
                    elif indentation_level > indentation_level_previous:
                        cs.i -= indentation_level + 1
                        node_next = state_line_beginning(indentation_level)
                        node_line.target = node_next
                        continue
                    elif indentation_level < indentation_level_previous:
                        cs.i -= indentation_level + 1
                        break
                cs.next()
            return node
        
        return state_line_beginning(0)
    
    def read_schema_main():
        with open("./README.md", "r") as f:
            data_block_header = ""
            data_block = ""
            is_in_data_block = False
            is_example = False
            root_node_disjunction = NodeDisjunction(possibilities=[])
            for line_n, line in enumerate(f, start=1):
                if line.startswith("##"):
                    data_block_header = line.replace("#", "").replace("\n", "").strip()
                    is_example = False
                elif line == "example:\n":
                    is_example = True
                elif line == "```\n":
                    is_in_data_block = not is_in_data_block
                    if not is_in_data_block and not is_example:
                        node = parse_data_block(data_block)
                        root_node_disjunction.possibilities.append(node)
                        data_block_header = ""
                        data_block = ""
                        is_example = False
                elif data_block_header != "" and not is_example and is_in_data_block:
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

if __name__ == "__main__":
    result = validate(yaml_to_validate="./tests/veld_yaml_files/code_barebone_valid.yaml")
    result = validate(yaml_to_validate="./tests/veld_yaml_files/data_barebone_valid.yaml")
    pass
    