import unittest
import xml.etree.ElementTree as ET
from io import StringIO
from config_parser import ConfigParser


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def normalize_xml(self, xml_str):
        """Утилита для нормализации XML строки (удаление пробелов) для сравнения."""
        return ''.join(xml_str.split())

    def test_remove_comments(self):
        """Тест на удаление комментариев."""
        config = """
        REM Это комментарий
        dict(
            123 = "value1", /* еще комментарий */
            456 = "value2"
        )
        """
        root = self.parser.parse(config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">value1</item>
        <item name="456">value2</item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

    def test_constants_declaration_and_usage(self):
        """Тест на объявление и использование констант."""
        config = """
        8080 -> port;
        dict(
            123 = $port$,
            456 = "test"
        )
        """
        root = self.parser.parse(config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">8080</item>
        <item name="456">test</item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

    def test_nested_dictionaries(self):
        """Тест на вложенные словари."""
        config = """
        dict(
            123 = dict(
                456 = "inner_value1",
                789 = "inner_value2"
            ),
            456 = dict(
                789 = "test"
            )
        )
        """
        root = self.parser.parse(config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">
            <dict>
                <item name="456">inner_value1</item>
                <item name="789">inner_value2</item>
            </dict>
        </item>
        <item name="456">
            <dict>
                <item name="789">test</item>
            </dict>
        </item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

    def test_syntax_error(self):
        """Тест на синтаксические ошибки."""
        # Тест на неправильный тип ключа (строка)
        config1 = """
        dict(
            key = "value"  /* Ключ не может быть строкой */
        )
        """
        with self.assertRaises(SyntaxError):
            self.parser.parse(config1)

        # Тест на пропущенные кавычки в значении
        config2 = """
        dict(
            123 = value  /* Пропущены кавычки */
        )
        """
        with self.assertRaises(SyntaxError):
            self.parser.parse(config2)

    def test_realistic_configurations(self):
        """Тесты с примерами из реальных предметных областей."""
        # 1. Конфигурация веб-сервера
        web_server_config = """
        dict(
            123 = "localhost",
            456 = 8080,
            789 = true
        )
        """
        root = self.parser.parse(web_server_config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">localhost</item>
        <item name="456">8080</item>
        <item name="789">True</item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

    def test_syntax_error(self):
        """Тест на синтаксические ошибки."""
        config = "dict(key1 = 'value1', key2)"  # Пропущено '='
        with self.assertRaises(SyntaxError):
            self.parser.parse(config)

    def test_realistic_configurations(self):
        """Тесты с примерами из реальных предметных областей."""
        # 1. Конфигурация веб-сервера
        web_server_config = """
        dict(
            123 = "localhost",
            456 = 8080,
            789 = true
        )
        """
        root = self.parser.parse(web_server_config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">localhost</item>
        <item name="456">8080</item>
        <item name="789">True</item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

        # 2. Конфигурация базы данных
        db_config = """
        dict(
            123 = "test_db",
            456 = "admin",
            789 = "password123",
            1011 = dict(
                1213 = 3,
                1415 = 30
            )
        )
        """
        root = self.parser.parse(db_config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">test_db</item>
        <item name="456">admin</item>
        <item name="789">password123</item>
        <item name="1011">
            <dict>
                <item name="1213">3</item>
                <item name="1415">30</item>
            </dict>
        </item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

        # 3. Конфигурация приложения
        app_config = """
        dict(
            123 = "my_app",
            456 = "1.0.0",
            789 = dict(
                1011 = true,
                1213 = false
            )
        )
        """
        root = self.parser.parse(app_config)
        expected_xml = '''<configuration>
    <dict>
        <item name="123">my_app</item>
        <item name="456">1.0.0</item>
        <item name="789">
            <dict>
                <item name="1011">True</item>
                <item name="1213">False</item>
            </dict>
        </item>
    </dict>
</configuration>'''
        
        self.assertEqual(
            self.normalize_xml(ET.tostring(root, encoding='unicode')), 
            self.normalize_xml(expected_xml)
        )

if __name__ == '__main__':
    unittest.main()
