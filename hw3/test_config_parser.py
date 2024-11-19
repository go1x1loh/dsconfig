import unittest
from io import StringIO
import sys
from config_parser import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def test_constant_declaration(self):
        input_data = [
            "port -> 8080;",
            "host -> localhost;"
        ]
        xml_output = self.parser.parse(input_data)
        self.assertIn("<constant name=\"port\">8080</constant>", xml_output)
        self.assertIn("<constant name=\"host\">localhost</constant>", xml_output)

    def test_constant_evaluation(self):
        input_data = [
            "port -> 8080;",
            "$port$"
        ]
        xml_output = self.parser.parse(input_data)
       
