import unittest

import jsonschema
import yaml

from main import validate


TEST_FILES_PATH = "./tests/test_veld_yaml_files/"


class TestVeldMetadata(unittest.TestCase):
    
    def validate_veldmetadata_file(self, veld_metadata_file_path):
        with open(TEST_FILES_PATH + veld_metadata_file_path, "r") as veld_metadata_file:
            veld_metadata = yaml.safe_load(veld_metadata_file)
            validate(veld_metadata)
    
    def validate_veldmetadata_file_valid(self, veld_metadata_file_path):
        try:
            self.validate_veldmetadata_file(veld_metadata_file_path)
        except jsonschema.exceptions.ValidationError as err:
            self.fail(err)
                
    def validate_veldmetadata_file_invalid(self, veld_metadata_file_path):
        try:
            self.validate_veldmetadata_file(veld_metadata_file_path)
            self.fail("this should not be valid")
        except jsonschema.exceptions.ValidationError as err:
            pass
    
    def test_chain_barebone_valid(self):
        self.validate_veldmetadata_file_valid("test_chain_barebone_valid.yaml")
    
    def test_chain_barebone_invalid(self):
        self.validate_veldmetadata_file_invalid("test_chain_barebone_invalid.yaml")
    
    def test_code_barebone_valid(self):
        self.validate_veldmetadata_file_valid("test_code_barebone_valid.yaml")
    
    def test_code_barebone_invalid(self):
        self.validate_veldmetadata_file_invalid("test_code_barebone_invalid.yaml")
    
    def test_data_barebone_valid(self):
        self.validate_veldmetadata_file_valid("test_data_barebone_valid.yaml")
    
    def test_data_barebone_invalid(self):
        self.validate_veldmetadata_file_invalid("test_data_barebone_invalid.yaml")
        