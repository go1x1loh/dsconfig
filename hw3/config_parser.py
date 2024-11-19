import sys
import re
import xml.etree.ElementTree as ET

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, lines):
        root = ET.Element("configuration")
        for line in lines:
            line = line.strip()
            if line.startswith("REM") or line.startswith("/*"):
                continue  # Пропускаем комментарии
            elif re.match(r'^[a-zA-Z][_a-zA-Z0-9]*\s*->\s*[a-zA-Z][_a-zA-Z0-9]*;', line):
                self.handle_constant_declaration(line, root)
            elif re.match(r'^\$[a-zA-Z][_a-zA-Z0-9]*\$$', line):
                self.handle_constant_evaluation(line, root)
            elif line.startswith("dict("):
                self.handle_dictionary(line, root)
            else:
                raise SyntaxError(f"Синтаксическая ошибка: {line}")
        return ET.tostring(root, encoding='unicode')

    def handle_constant_declaration(self, line, root):
        match = re.match(r'([a-zA-Z][_a-zA-Z0-9]*)\s*->\s*([a-zA-Z][_a-zA-Z0-9]*);', line)
        if match:
            name = match.group(1)
            value = match.group(2)
            self.constants[name] = value
            ET.SubElement(root, "constant", name=name).text = value
        else:
            raise SyntaxError(f"Некорректное объявление константы: {line}")

    def handle_constant_evaluation(self, line, root):
        name = line[1:-1]
        if name in self.constants:
            ET.SubElement(root, "constant_evaluation", name=name).text = self.constants[name]
        else:
            raise NameError(f"Константа не найдена: {name}")

    def handle_dictionary(self, line, root):
        if not line.endswith(')'):
            raise SyntaxError(f"Некорректный словарь: {line}")
        
        dict_content = line[5:-1]  # Убираем 'dict(' и ')'
        items = [item.strip() for item in dict_content.split(',') if item.strip()]
        dict_element = ET.SubElement(root, "dictionary")
        
        for item in items:
            match = re.match(r'([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*([a-zA-Z0-9]+);?', item)
            if match:
                name = match.group(1)
                value = match.group(2)
                ET.SubElement(dict_element, "entry", name=name).text = value
            else:
                raise SyntaxError(f"Некорректная пара имя-значение в словаре: {item}")

def main(output_file):
    parser = ConfigParser()
    try:
        lines = sys.stdin.readlines()
        xml_output = parser.parse(lines)
        with open(output_file, 'w') as f:
            f.write(xml_output)
    except (SyntaxError, NameError) as e:
        print(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python config_parser.py <output_file>")
        sys.exit(1)

    output_file = sys.argv[1]
    main(output_file)
