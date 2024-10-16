import yaml


def validate(veld_metadata):
    
    def parse_data_block(data_block_str):
        
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
            
        data_block_str = clean_str(data_block_str)
        d = yaml.safe_load(data_block_str)
        return d
    
    def validate_main():
        with open("./README.md", "r") as f:
            is_example = False
            is_data = False
            data_block = ""
            for line_n, line in enumerate(f, start=1):
                if line == "example:\n":
                    is_example = True
                elif line == "```\n":
                    if not is_data:
                        is_data = True
                    elif is_data:
                        is_data = False
                        if is_example:
                            is_example = False
                        else:
                            data_block_dict = parse_data_block(data_block)
                            print(data_block_dict)
                            data_block = ""
                elif is_data and not is_example:
                    data_block += line
                    
    return validate_main()
        

if __name__ == "__main__":
    validate({})
