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
    
    def copy(self):
        node_copy = self.__class__.__new__(self.__class__)
        for k, v in self.__dict__.items():
            if isinstance(v, Node):
                v = v.copy()
            elif type(v) is list:
                v_sub_copy = []
                for v_sub in v:
                    if isinstance(v_sub, Node):
                        v_sub_copy.append(v_sub.copy())
                v = v_sub_copy
            node_copy.__dict__[k] = v
        return node_copy
    
    def __repr__(self):
        if self.content is None:
            return "<PRIMITIVE>"
        else:
            return str(self.content)
    
    def __str__(self):
        return self.__repr__()

    
@dataclass(repr=False)
class NodeMapping(Node):
    content: Union[Node, None] = None
    target: Union[Node, None] = None
    
    def __repr__(self):
        return str(f"{self.content}: {self.target}")
    
    
@dataclass(repr=False)
class NodeDict(Node):
    content: Union[List[NodeMapping], None] = None
    
    def __repr__(self):
        return str(", ".join([repr(nm) for nm in self.content]))
    
    
@dataclass(repr=False)
class NodeList(Node):
    content: Union[Node, None] = None
    
    def __repr__(self):
        return str(f"{{{self.content}}}")


@dataclass(repr=False)
class NodeDisjunction(Node):
    content: Union[List[Node], None] = None
    
    def __repr__(self):
        return str(" | ".join([repr(c) for c in self.content]))
    
    
@dataclass(repr=False)
class NodeVariableDefinition(Node):
    content: Union[Node, None] = None
    target: Union[Node, None] = None
    
    def __repr__(self):
        return str(f"{self.content}::= {self.target}")


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
                    if optional_open:
                        node.is_optional = True
                elif cs.char == "{":
                    list_open = True
                elif cs.char == "}":
                    list_close = True
                    if list_open:
                        node = NodeList(content=node)
                elif cs.char == ":":
                    cs.next()
                    if cs.char == ":":
                        cs.next()
                        if cs.char == "=":
                            cs.next()
                            node = NodeVariableDefinition(content=node)
                            node.content.is_variable = False
                            node_next = state_next()
                            if type(node_next) is NodeMapping:
                                node_next = NodeDict(
                                    content=[node_next],
                                    is_optional=node_next.is_optional
                                )
                            node.target = node_next
                    else:
                        if cs.char == " " or cs.char == "\n":
                            node = NodeMapping(content=node)
                            node.target = state_next()
                            if optional_open and not optional_close:
                                node.is_optional = True
                            if list_open and not list_close:
                                node = NodeDict(content=[node])
                    continue
                elif cs.char == "|":
                    cs.next()
                    node = NodeDisjunction(content=[node])
                    node_next = state_next()
                    if type(node_next) is NodeDisjunction:
                        for node_next_possible in node_next.content:
                            node.content.append(node_next_possible)
                    else:
                        node.content.append(node_next)
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
                        if (
                            type(node_line) is NodeMapping
                            or (type(node_line) is Node and node_line.is_variable)
                        ):
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
                        if type(node) is NodeDict:
                            node.is_optional = all([n.is_optional for n in node.content])
                        cs.i -= indentation_level + 1
                        break
                cs.next()
            return node
        
        return state_line_beginning(0)
    
    def resolve_variables(schema_with_variables):
        
        def resolve_variables_recursively(node: Node):
            if type(node) is NodeMapping:
                node.content = resolve_variables_recursively(node.content)
                node.target = resolve_variables_recursively(node.target)
            elif type(node) is NodeDict:
                for node_sub in node.content:
                    node_sub = resolve_variables_recursively(node_sub)
            elif type(node) is NodeDisjunction:
                for node_sub in node.content:
                    node_sub = resolve_variables_recursively(node_sub)
            elif type(node) is NodeList:
                node.content = resolve_variables_recursively(node.content)
            elif type(node) is Node:
                if node.is_variable:
                    node.is_variable = False
                    if node.content in schema_with_variables["variables"]:
                        node_var_instance = schema_with_variables["variables"][node.content]
                        node_var_instance = node_var_instance.copy()
                        is_optional = node.is_optional
                        node = resolve_variables_recursively(node_var_instance)
                        node.is_optional = is_optional
                    else:
                        node.content = None
            return node
        
        def resolve_variables_main():
            schema = {}
            for k, v in schema_with_variables["velds"].items():
                schema[k] = resolve_variables_recursively(v)
            return schema
        
        return resolve_variables_main()
    
    def read_schema_main():
        with open("./README.md", "r") as f:
            data_block_header = ""
            data_block_counter = 0
            data_block = ""
            is_example = False
            schema_with_variables = {
                "velds": {
                    "data": None,
                    "code": None,
                    "chain": None,
                },
                "variables": {},
            }
            for line_n, line in enumerate(f, start=1):
                if line.startswith("###"):
                    data_block_header = line.replace("#", "").replace("\n", "").strip().split(" ")[0]
                    is_example = False
                elif data_block_header != "":
                    if line == "example:\n":
                        is_example = True
                    elif not is_example:
                        if line.startswith("```"):
                            data_block_counter += 1
                        elif data_block_counter == 1:
                            data_block += line
                        if data_block_counter == 2:
                            node = parse_data_block(data_block)
                            if type(node) is NodeVariableDefinition:
                                schema_with_variables["variables"][node.content.content] = node.target
                            else:
                                schema_with_variables["velds"][data_block_header] = node
                            data_block_header = ""
                            data_block_counter = 0
                            data_block = ""
                            is_example = False
            schema = resolve_variables(schema_with_variables)
            return schema
    
    return read_schema_main()


def validate(dict_to_validate: dict = None, yaml_to_validate: str = None):

    def validate_dict(obj_to_validate, node: Node, path=""):
        
        def handle_node_disjunction(obj_to_validate, node: NodeDisjunction, path):
            result_list = []
            is_one_valid = False
            for possible_node in node.content:
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
                elif not target.is_optional and not target.content is None:
                    return (False, f"non-optional value: '{target}' missing at: {path_sub}/")
                return (True, None)
            
            if type(obj_to_validate) is not dict:
                return (False, f"is not dict at: {path}/")
            else:
                node_keys_variables = []
                for node_mapping in node.content:
                    if type(node_mapping) is NodeMapping:
                        node_key = node_mapping.content.content
                        node_target = node_mapping.target
                        if node_mapping.content.content is None:
                            node_keys_variables.append(node_mapping)
                            continue
                        if node_key in obj_to_validate:
                            obj_value = obj_to_validate.pop(node_key)
                            path_sub = path + "/" + node_key
                            result = go_to_target(obj_value, node_target, path_sub)
                            if not result[0]:
                                return result
                        elif not node_mapping.is_optional:
                            return (False, f"non-optional key missing: '{node_key}', at: {path}/")
                for node_mapping in node_keys_variables:
                    node_target = node_mapping.target
                    obj_key = next(iter(obj_to_validate.keys()))
                    obj_value = obj_to_validate.pop(obj_key)
                    path_sub = path + "/" + obj_key
                    result = go_to_target(obj_value, node_target, path_sub)
                    if not result[0]:
                        return result
                
                other_elements_allowed = False
                for node_sub in node.content:
                    if type(node_sub) is NodeMapping:
                        if node_sub.content.content is None:
                            other_elements_allowed = True
                    elif type(node_sub) is Node and node_sub.content is None:
                        other_elements_allowed = True
                if len(obj_to_validate) != 0 and not other_elements_allowed:
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
            return (True, None)
        
        def validate_dict_main(obj_to_validate, node: Node, path):
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
        
        return validate_dict_main(obj_to_validate, node, path)

    def validate_main(dict_to_validate: dict, yaml_to_validate: str):
        if dict_to_validate is None == yaml_to_validate is None:
            raise Exception(f"two parameters passed: {dict_to_validate} and {yaml_to_validate}")
        elif yaml_to_validate is not None:
            with open(yaml_to_validate, "r") as f:
                dict_to_validate = yaml.safe_load(f)
        schema = read_schema()
        if dict_to_validate is None:
            return (False, "empty dict")
        if "x-veld" not in dict_to_validate:
            return (False, "root node x-veld missing")
        x_veld = dict_to_validate["x-veld"]
        if x_veld is None:
            return (False, "entry under x-veld is empty")
        if len(x_veld) != 1:
            return (False, f"multiple entries found under x-veld: {x_veld}")
        veld_type = None
        for k in x_veld.keys():
            if k in ["data", "code", "chain"]:
                veld_type = k
        if veld_type is None:
            return (False, f"neither data, code, or chain: {veld_type}")
        return validate_dict(dict_to_validate, schema[veld_type])
            
    return validate_main(dict_to_validate, yaml_to_validate)
