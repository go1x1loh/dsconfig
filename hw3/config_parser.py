import re
import argparse
import xml.etree.ElementTree as ET
import sys
from xml.dom import minidom


class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        text = self._remove_comments(text)
        lines_iter = iter(text.splitlines())
        result = ET.Element("config")

        for line in lines_iter:
            line = line.strip()
            if not line:
                continue
            if "->" in line:
                self._process_constant(line)
            elif line.startswith("dict("):
                result.append(self._parse_dict(lines_iter))
            else:
                raise SyntaxError(f"Unexpected line: {line}")
        return result

    def _remove_comments(self, text):
        text = re.sub(r"REM.*", "", text)  # Однострочные комментарии
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)  # Многострочные комментарии
        return text

    def _process_constant(self, line):
        match = re.match(r"(.+?)\s*->\s*([a-zA-Z][_a-zA-Z0-9]*)\s*;", line)
        if not match:
            raise SyntaxError(f"Invalid constant declaration: {line}")
        value, name = match.groups()
        value = self._evaluate(value)
        self.constants[name] = value

    def _evaluate(self, expr):
        # Нормализация значений true/false
        expr = self._normalize_values(expr)
        expr = re.sub(r"\$([a-zA-Z][_a-zA-Z0-9]*)\$", 
                      lambda m: str(self.constants.get(m.group(1), f"Unknown constant: {m.group(1)}")), 
                      expr)
        try:
            return eval(expr)
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expr}': {e}")

    def _normalize_values(self, expr):
        """Заменяет 'true' на 'True', 'false' на 'False'."""
        return expr.replace("true", "True").replace("false", "False")

    def _parse_dict(self, lines_iter):
        """Парсит словарь, начиная с dict( и заканчивая )"""
        dict_element = ET.Element("dict")
        content = ""

        for line in lines_iter:
            line = line.strip()
            if line.endswith(")"):  # Конец словаря
                content += line[:-1]  # Добавляем содержимое без ")"
                break
            content += line  # Добавляем строки внутри словаря

        for pair in content.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if "=" not in pair:
                raise SyntaxError(f"Invalid key-value pair: {pair}")
            key, value = pair.split("=", 1)
            key, value = key.strip(), value.strip()
            if not re.match(r"[a-zA-Z][_a-zA-Z0-9]*", key):
                raise SyntaxError(f"Invalid key: {key}")
            value = self._evaluate(value)
            item = ET.SubElement(dict_element, "item", name=key)
            item.text = str(value)
        return dict_element


def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык в XML.")
    parser.add_argument("output", help="Путь к выходному XML-файлу.")
    args = parser.parse_args()

    # Чтение входного текста через stdin
    input_text = sys.stdin.read()

    config_parser = ConfigParser()
    try:
        root = config_parser.parse(input_text)

        # Форматируем XML
        rough_string = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(rough_string)
        pretty_xml = parsed.toprettyxml(indent="  ")

        # Записываем отформатированный XML в файл
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        print(f"XML успешно записан в {args.output}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

