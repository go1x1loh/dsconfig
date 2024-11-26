import argparse
import re
import sys
from typing import Dict, Any
import xml.etree.ElementTree as ET
from io import StringIO

class ConfigParser:
    def __init__(self):
        self.constants: Dict[str, Any] = {}

    def parse(self, input_text: str) -> ET.Element:
        # Remove comments first
        text_without_comments = self.remove_comments(input_text)
        
        # Split into logical lines
        lines = [line.strip() for line in text_without_comments.splitlines()]
        lines = [line for line in lines if line]  # Remove empty lines
        
        root = ET.Element('configuration')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if '->' in line:  # Constant declaration
                self.handle_constant_declaration(line)
            elif line.startswith('dict('):
                # Collect all lines until matching closing parenthesis
                dict_lines = [line]
                paren_count = line.count('(') - line.count(')')
                while paren_count > 0 and i + 1 < len(lines):
                    i += 1
                    dict_lines.append(lines[i])
                    paren_count += lines[i].count('(') - lines[i].count(')')
                dict_elem = self.handle_dict('\n'.join(dict_lines))
                root.append(dict_elem)
            elif line.startswith('$') and line.endswith('$'):
                value = self.resolve_constant(line)
                const_elem = ET.SubElement(root, 'constant')
                const_elem.text = str(value)
            else:
                raise SyntaxError(f"Invalid syntax at line: {line}")
            i += 1
        
        return root

    def remove_comments(self, text: str) -> str:
        # Remove REM comments
        lines = []
        for line in text.splitlines():
            if not line.strip().startswith('REM'):
                lines.append(line)
        text = '\n'.join(lines)
        
        # Remove /* */ comments, but preserve them in strings
        result = []
        in_comment = False
        in_string = False
        string_char = None
        i = 0
        
        while i < len(text):
            if not in_string and text[i:i+2] == '/*':
                in_comment = True
                i += 2
                continue
            elif not in_string and text[i:i+2] == '*/':
                in_comment = False
                i += 2
                continue
            elif not in_comment and text[i] in '"\'':
                if not in_string:
                    in_string = True
                    string_char = text[i]
                elif text[i] == string_char:
                    in_string = False
                    string_char = None
                result.append(text[i])
            elif not in_comment:
                result.append(text[i])
            i += 1
        
        return ''.join(result)

    def handle_constant_declaration(self, line: str) -> None:
        value, name = map(str.strip, line.split('->'))
        name = name.rstrip(';')
        
        if not re.match(r'^[a-zA-Z][_a-zA-Z0-9]*$', name):
            raise SyntaxError(f"Invalid constant name: {name}")
        
        # Try to parse value as number
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                # If not a number, check if it's a dictionary
                if value.startswith('dict('):
                    value = self.handle_dict(value)
                else:
                    raise SyntaxError(f"Invalid constant value: {value}")
        
        self.constants[name] = value

    def handle_dict(self, text: str) -> ET.Element:
        if not text.startswith('dict(') or not text.rstrip().endswith(')'):
            raise SyntaxError(f"Invalid dictionary syntax: {text}")
        
        # Extract content between dict( and )
        content = text[5:-1].strip()
        
        dict_elem = ET.Element('dict')
        
        if not content:
            return dict_elem
        
        # First, normalize line endings and remove extra whitespace
        content = ' '.join(line.strip() for line in content.splitlines())
        
        # Split content into key-value pairs
        pairs = []
        current = []
        paren_count = 0
        quote_char = None
        in_value = False
        key = None
        
        i = 0
        while i < len(content):
            char = content[i]
            
            # Handle quotes
            if char in '"\'':
                if quote_char is None:
                    quote_char = char
                elif char == quote_char and (i == 0 or content[i-1] != '\\'):
                    quote_char = None
                current.append(char)
            # Handle nested structures when not in quotes
            elif quote_char is None:
                if char == '=' and not in_value:
                    key = ''.join(current).strip()
                    current = []
                    in_value = True
                elif char == '(':
                    paren_count += 1
                    current.append(char)
                elif char == ')':
                    paren_count -= 1
                    current.append(char)
                elif char == ',' and paren_count == 0 and in_value:
                    value = ''.join(current).strip()
                    pairs.append((key, value))
                    current = []
                    in_value = False
                else:
                    current.append(char)
            # Add character if in quotes
            else:
                current.append(char)
            
            i += 1
        
        if current and in_value:
            value = ''.join(current).strip()
            pairs.append((key, value))
        
        # Process each key-value pair
        for key, value in pairs:
            if not key or not value:
                continue
            
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Handle nested dictionary
            if value.startswith('dict('):
                item = ET.SubElement(dict_elem, 'item', {'name': key})
                nested_dict = self.handle_dict(value)
                item.append(nested_dict)
            else:
                # Handle constant reference
                if value.startswith('$') and value.endswith('$'):
                    value = str(self.resolve_constant(value))
                elif value.lower() == 'true':
                    value = 'True'
                elif value.lower() == 'false':
                    value = 'False'
                
                item = ET.SubElement(dict_elem, 'item', {'name': key})
                item.text = value
        
        return dict_elem

    def resolve_constant(self, line: str) -> Any:
        name = line[1:-1]  # Remove $
        if name not in self.constants:
            raise SyntaxError(f"Undefined constant: {name}")
        return self.constants[name]

def main():
    parser = argparse.ArgumentParser(description='Convert custom config language to XML.')
    parser.add_argument('output_file', type=str, help='Output XML file path')
    args = parser.parse_args()

    try:
        input_text = sys.stdin.read()
        config_parser = ConfigParser()
        output = config_parser.parse(input_text)
        
        with open(args.output_file, 'w') as f:
            tree = ET.ElementTree(output)
            tree.write(f, encoding='unicode', xml_declaration=True)
        print(f"Successfully wrote output to {args.output_file}")
    except SyntaxError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
