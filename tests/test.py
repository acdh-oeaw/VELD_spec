import os
import unittest

from veld_spec import validate


class TestVeldMetadata(unittest.TestCase):
    
    def test_chain_barebone_valid(self):
        result = validate(yaml_to_validate="./tests/veld_yaml_files/chain_barebone_valid.yaml")
        self.assertTrue(result[0])
    
    def test_chain_barebone_invalid(self):
        result = validate(yaml_to_validate="./tests/veld_yaml_files/chain_barebone_invalid.yaml")
        self.assertFalse(result[0])
    
    def test_code_barebone_valid(self):
        result = validate(yaml_to_validate="./tests/veld_yaml_files/code_barebone_valid.yaml")
        self.assertTrue(result[0])
    
    def test_code_barebone_invalid(self):
        result = validate(yaml_to_validate="./tests/veld_yaml_files/code_barebone_invalid.yaml")
        self.assertFalse(result[0])
    
    def test_data_barebone_valid(self):
        result = validate(yaml_to_validate="./tests/veld_yaml_files/data_barebone_valid.yaml")
        self.assertTrue(result[0])
    
    def test_data_barebone_invalid(self):
        result = validate(yaml_to_validate="./tests/veld_yaml_files/data_barebone_invalid.yaml")
        self.assertFalse(result[0])
        
    def test_production_velds(self):
        production_velds_folder = "./tests/veld_yaml_files/production_velds/"
        num_correct = 0
        num_incorrect = 0
        for veld_file in os.listdir(production_velds_folder):
            veld_file_path = production_velds_folder + "/" + veld_file
            result = validate(yaml_to_validate=veld_file_path)
            if not result[0]:
                num_incorrect += 1
                print(veld_file_path)
                print(result[1])
            else:
                num_correct += 1
        print("num_correct:", num_correct)
        print("num_incorrect:", num_incorrect)


if __name__ == "__main__":
    unittest.main()