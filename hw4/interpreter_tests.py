import unittest
import tempfile
import os
import csv
from interpreter import interpret  # Импортируем функцию interpret

class InterpreterTests(unittest.TestCase):
    def test_read_command(self):
        binary_data = bytearray([0x04, 0x00, 0x00, 0x01, 0x17, 0x00, 0x00, 0x02, 0x3a, 0x00, 0x00])
        memory_range = (0, 1024)
        expected_result = [['Address', 'Value']] + [[i, 0] for i in range(1024)]
        expected_result[279][1] = 570
        self._test_interpreter(binary_data, memory_range, expected_result)

    def test_write_command(self):
        binary_data = bytearray([0x03, 0x00, 0x00, 0x01, 0xf6, 0x00, 0x00, 0x03, 0xa7, 0x00, 0x00])
        memory_range = (0, 1024)
        expected_result = [['Address', 'Value']] + [[i, 0] for i in range(1024)]
        expected_result[935][1] = 502
        self._test_interpreter(binary_data, memory_range, expected_result)

    def test_le_command(self):
        binary_data = bytearray([0x06, 0x00, 0x00, 0x03, 0xaa, 0x00, 0x00, 0x00, 0x6f, 0x00, 0x00, 0x02, 0xa5])
        memory_range = (0, 1024)
        expected_result = [['Address', 'Value']] + [[i, 0] for i in range(1024)]
        expected_result[938][1] = 1  # Assuming 111 <= 677
        self._test_interpreter(binary_data, memory_range, expected_result)

    def _test_interpreter(self, binary_data, memory_range, expected_result):
        with tempfile.NamedTemporaryFile(delete=False) as binary_file:
            binary_file.write(binary_data)
            binary_file_name = binary_file.name

        with tempfile.NamedTemporaryFile(delete=False) as result_file:
            result_file_name = result_file.name

        interpret(binary_file_name, result_file_name, memory_range)

        with open(result_file_name, 'r') as f:
            actual_result = list(csv.reader(f))

        self.assertEqual(actual_result, expected_result)

        os.remove(binary_file_name)
        os.remove(result_file_name)

if __name__ == '__main__':
    unittest.main()

