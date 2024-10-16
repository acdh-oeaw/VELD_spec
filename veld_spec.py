import yaml


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
    
    def parse_data_block(data_block_header, data_block_str):
        data_block_str = clean_str(data_block_str)
        data_block_dict = yaml.safe_load(data_block_str)
        data_block_dict = {data_block_header: data_block_dict}
        data_block_dict = clean_dict_recursively(data_block_dict)
        return data_block_dict
    
    def validate_main():
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
                        data_block_dict = parse_data_block(data_block_header, data_block)
                        print(data_block_dict)
                        data_block_header = ""
                        data_block = ""
                        is_example = False
                    is_data_block = not is_data_block
                elif is_data_block and data_block_header != "":
                    data_block += line
                    
    return validate_main()
        

if __name__ == "__main__":
    validate({})
