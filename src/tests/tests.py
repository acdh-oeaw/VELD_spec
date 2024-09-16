import unittest

import jsonschema
import yaml

from main import validate


TEST_FILES_PATH = "./tests/test_veld_yaml_files/"


class TestVeldMetadata(unittest.TestCase):
    
    def validate_veldmetadata_file(self, veld_metadata_file_path):
        with open(TEST_FILES_PATH + veld_metadata_file_path, "r") as veld_metadata_file:
            veld_metadata = yaml.safe_load(veld_metadata_file)
            try:
                validate(veld_metadata)
            except jsonschema.exceptions.ValidationError as err:
                self.fail(err)
    
    def test_1(self):
        self.validate_veldmetadata_file("test_1.yaml")
    
    def test_2(self):
        self.validate_veldmetadata_file("test_2.yaml")
        