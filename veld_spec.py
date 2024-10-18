from dataclasses import dataclass
from typing import List, Union, Dict



@dataclass
class Node:
    is_optional: bool = False
    is_variable: bool = False
    content: Union[str, None] = None
    
@dataclass
class NodeMapping(Node):
    content: Union[str, None] = None
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
                    content="x-veld",
                    target=NodeDict(
                        content=[
                            NodeMapping(
                                content="data",
                                target=NodeDict(
                                    content=[
                                        NodeMapping(
                                            content="description",
                                            target=Node(
                                                is_optional=True,
                                                content=None
                                            )
                                        ),
                                        NodeMapping(
                                            content="topics",
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
                                            content="additional",
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
                    content="x-veld",
                    target=NodeDict(
                        content=[
                            NodeMapping(
                                content="code",
                                target=NodeDict(
                                    content=[
                                        NodeMapping(
                                            content="description",
                                            target=Node(
                                                is_optional=True,
                                                content=None
                                            )
                                        ),
                                        NodeMapping(
                                            content="topics",
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
                                            content="additional",
                                            target=Node(
                                                is_optional=True,
                                                content=None
                                            )
                                        ),
                                    ]
                                )
                            )
                        ]
                    )
                ),
                NodeMapping(
                    content="services",
                    target=NodeDict(
                        content=[
                            NodeMapping(
                                content=None,
                                target=NodeDict(
                                    content=[
                                        NodeMapping(
                                            content="compose_definition",
                                            target=None,
                                        ),
                                        NodeMapping(
                                            content="volumes",
                                            is_optional=True,
                                            target=None,
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




pass


def validate(veld_metadata):
    
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
    
    def parse_data_block(data_block_line_list):
        
        def state_key(line):
            key = ""
            is_optional_counter = 0
            for char_i, char in enumerate(line):
                if char == "[":
                    is_optional_counter += 1
                elif char != ":" and char != " ":
                    key += char
                else:
                    pass
                    
            
        
        def state_start(line):
            indentation_level = 0
            for char_i, char in enumerate(line):
                if char == " ":
                    indentation_level += 1
                else:
                    state_key(line[char_i+1:])
                    
        
        
        data_block_dict = {}
        for line_i, line in enumerate(data_block_line_list):
            is_beginning = True
            is_variable = False
            is_key = True
            is_optional_counter = 0
            indentation_level = 0
            key = ""
            value = ""
            for char in line:
                if is_beginning and char == " ":
                    indentation_level += 1
                elif is_beginning and char != " ":
                    is_beginning = False
                elif not is_beginning:
                    if char == "[":
                        is_optional_counter += 1
                    elif char == "]":
                        is_optional_counter -= 1
                    elif char == "<":
                        is_variable = True
                    elif char == ">":
                        is_variable = False
                    elif is_key and char != ":" and char != " ":
                        key += char
                    elif is_key and char == ":":
                        is_key = False
                        is_value = True
                    elif is_value and char != " ":
                        value += char
                    else:
                        continue
                        
                
        
        return data_block_dict
    
    def validate_main():
        schema_dict = {}
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
                        data_block_dict = {data_block_header: parse_data_block(data_block.split("\n"))}
                        schema_dict.update(data_block_dict)
                        data_block_header = ""
                        data_block = ""
                        is_example = False
                    is_data_block = not is_data_block
                elif is_data_block and data_block_header != "":
                    data_block += line
                    
        pass
        
    return validate_main()
    

if __name__ == "__main__":
    validate({})
