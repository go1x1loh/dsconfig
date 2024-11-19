import unittest
import xml.etree.ElementTree as ET
from io import StringIO
from config_parser import ConfigParser  # Импортируем наш парсер


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def parse_to_dict(self, config_text):
        """Утилита для преобразования XML-результата в словарь для удобства проверки."""
        root = self.parser.parse(config_text)
        result = {}
        for dict_elem in root.findall("dict"):
            for item in dict_elem.findall("item"):
                name = item.attrib['name']
                result[name] = item.text
        return result

    def test_remove_comments(self):
        """Тест на удаление комментариев."""
        config = """
        REM Это комментарий
        dict(
            key1 = "value1" /* еще комментарий */
            key2 = "value2"
        )
        """
        expected = {'key1': 'value1', 'key2': 'value2'}
        result = self.parse_to_dict(config)
        self.assertEqual(result, expected)

    def test_constants_declaration_and_usage(self):
        """Тест на объявление и использование констант."""
        config = """
        8080 -> port;
        dict(
            key1 = $port$,
            key2 = "test"
        )
        """
        expected = {'key1': '8080', 'key2': 'test'}
        result = self.parse_to_dict(config)
        self.assertEqual(result, expected)

    def test_nested_dictionaries(self):
        """Тест на вложенные словари."""
        config = """
        dict(
            key1 = dict(
                inner_key1 = 123,
                inner_key2 = "inner_value"
            ),
            key2 = "outer_value"
        )
        """
        root = self.parser.parse(config)
        nested_dict = root.find(".//item[@name='key1']/dict")
        inner_key1 = nested_dict.find("item[@name='inner_key1']").text
        inner_key2 = nested_dict.find("item[@name='inner_key2']").text

        self.assertEqual(inner_key1, '123')
        self.assertEqual(inner_key2, 'inner_value')

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
            host = "localhost",
            port = 8080,
            enable_ssl = true
        )
        """
        web_expected = {'host': 'localhost', 'port': '8080', 'enable_ssl': 'True'}
        self.assertEqual(self.parse_to_dict(web_server_config), web_expected)

        # 2. Конфигурация базы данных
        db_config = """
        dict(
            db_name = "test_db",
            user = "admin",
            password = "password123",
            nested_config = dict(
                retries = 3,
                timeout = 30
            )
        )
        """
        root = self.parser.parse(db_config)
        db_name = root.find(".//item[@name='db_name']").text
        nested_retries = root.find(".//item[@name='nested_config']/dict/item[@name='retries']").text

        self.assertEqual(db_name, "test_db")
        self.assertEqual(nested_retries, '3')

        # 3. Конфигурация приложения
        app_config = """
        dict(
            app_name = "my_app",
            version = "1.0.0",
            features = dict(
                feature1 = true,
                feature2 = false
            )
        )
        """
        app_expected = {'app_name': 'my_app', 'version': '1.0.0', 'feature1': 'True', 'feature2': 'False'}
        root = self.parser.parse(app_config)
        app_results = self.parse_to_dict(app_config)

        self.assertEqual(app_results['app_name'], app_expected['app_name'])
        self.assertEqual(app_results['version'], app_expected['version'])
        self.assertEqual(app_results['feature1'], app_expected['feature1'])


