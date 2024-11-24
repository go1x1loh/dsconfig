import argparse
import re
import sys
from typing import Dict, Any

class ConfigParser:
    def __init__(self):
        self.constants: Dict[str, Any] = {}

    def parse(self, input_text: str) -> str:
        # Remove comments first
        text_without_comments = self.remove_comments(input_text)
        
        # Split into logical lines
        lines = [line.strip() for line in text_without_comments.splitlines()]
        lines = [line for line in lines if line]  # Remove empty lines
        
        xml_elements = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_elements.append('<configuration>')
        
        i = 0
        section_count = 0
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
                section_count += 1
                xml_elements.append(f'<section id="{section_count}">')
                xml_elements.append(self.handle_dict('\n'.join(dict_lines)))
                xml_elements.append('</section>')
            elif line.startswith('$') and line.endswith('$'):
                value = self.resolve_constant(line)
                xml_elements.append(f"<constant>{value}</constant>")
            else:
                raise SyntaxError(f"Invalid syntax at line: {line}")
            i += 1
        
        xml_elements.append('</configuration>')
        return '\n'.join(xml_elements)

    def remove_comments(self, text: str) -> str:
        # Remove REM comments
        lines = []
        for line in text.splitlines():
            if not line.strip().startswith('REM'):
                lines.append(line)
        text = '\n'.join(lines)
        
        # Remove /* */ comments
        text = re.sub(r'/\*[\s\S]*?\*/', '', text)
        return text

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

    def handle_dict(self, text: str) -> str:
        if not text.startswith('dict(') or not text.rstrip().endswith(')'):
            raise SyntaxError(f"Invalid dictionary syntax: {text}")
        
        # Extract content between dict( and )
        content = text[5:-1].strip()
        
        if not content:
            return "<dict/>"
        
        items = []
        current_item = []
        paren_count = 0
        
        # Split by commas, but handle nested structures
        for char in content:
            if char == '(' or char == '{':
                paren_count += 1
            elif char == ')' or char == '}':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                items.append(''.join(current_item).strip())
                current_item = []
                continue
            current_item.append(char)
        
        if current_item:
            items.append(''.join(current_item).strip())
        
        dict_items = {}
        for item in items:
            if not item:
                continue
            if '=' not in item:
                raise SyntaxError(f"Invalid dictionary item: {item}")
            
            key, value = map(str.strip, item.split('=', 1))
            
            if not re.match(r'^[a-zA-Z][_a-zA-Z0-9]*$', key):
                raise SyntaxError(f"Invalid dictionary key: {key}")
            
            # Try to parse value
            try:
                parsed_value = int(value)
            except ValueError:
                try:
                    parsed_value = float(value)
                except ValueError:
                    if value.startswith('dict('):
                        parsed_value = self.handle_dict(value)
                    elif value.startswith('$') and value.endswith('$'):
                        parsed_value = self.resolve_constant(value)
                    else:
                        parsed_value = value
            
            dict_items[key] = parsed_value
        
        return self.dict_to_xml(dict_items)

    def dict_to_xml(self, dict_items: Dict[str, Any]) -> str:
        if not dict_items:
            return "<dict/>"
        
        xml_lines = ["<dict>"]
        for key, value in dict_items.items():
            if isinstance(value, (int, float)):
                xml_lines.append(f"  <{key}>{value}</{key}>")
            elif isinstance(value, str) and value.startswith('<dict>'):
                # Handle nested dictionary
                indented_value = '\n'.join(f"  {line}" for line in value.splitlines())
                xml_lines.append(f"  <{key}>\n{indented_value}\n  </{key}>")
            else:
                xml_lines.append(f"  <{key}>{value}</{key}>")
        xml_lines.append("</dict>")
        return '\n'.join(xml_lines)

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
            f.write(output)
        print(f"Successfully wrote output to {args.output_file}")
    except SyntaxError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
