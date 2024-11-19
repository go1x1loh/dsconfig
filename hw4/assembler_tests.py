import unittest
import struct
import tempfile
import os
from assembler import assemble  # Импортируем функцию assemble

class AssemblerTests(unittest.TestCase):
    def test_read_command(self):
        input_data = "READ 279 570"
        expected_output = bytearray([0x04, 0x00, 0x00, 0x01, 0x17, 0x00, 0x00, 0x02, 0x3a, 0x00, 0x00])
        self._test_assembler(input_data, expected_output)

    def test_write_command(self):
        input_data = "WRITE 502 935"
        expected_output = bytearray([0x03, 0x00, 0x00, 0x01, 0xf6, 0x00, 0x00, 0x03, 0xa7, 0x00, 0x00])
        self._test_assembler(input_data, expected_output)

    def test_le_command(self):
        input_data = "LE 938 111 677"
        expected_output = bytearray([0x06, 0x00, 0x00, 0x03, 0xaa, 0x00, 0x00, 0x00, 0x6f, 0x00, 0x00, 0x02, 0xa5])
        self._test_assembler(input_data, expected_output)

    def _test_assembler(self, input_data, expected_output):
        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_file.write(input_data.encode())
            input_file_name = input_file.name

        with tempfile.NamedTemporaryFile(delete=False) as output_file:
            output_file_name = output_file.name

        with tempfile.NamedTemporaryFile(delete=False) as log_file:
            log_file_name = log_file.name

        assemble(input_file_name, output_file_name, log_file_name)

        with open(output_file_name, 'rb') as f:
            actual_output = f.read()

        self.assertEqual(actual_output, expected_output)

        os.remove(input_file_name)
        os.remove(output_file_name)
        os.remove(log_file_name)

if __name__ == '__main__':
    unittest.main()

