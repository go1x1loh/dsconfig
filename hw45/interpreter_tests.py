import unittest
import os
import tempfile
from interpreter import UVMInterpreter
from assembler import pack_instruction

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = UVMInterpreter()
        self.test_dir = tempfile.mkdtemp()
        self.binary_file = os.path.join(self.test_dir, 'test.bin')
        self.output_file = os.path.join(self.test_dir, 'output.csv')

    def test_load_instruction(self):
        """Test LOAD instruction execution"""
        # LOAD 16 42 (Load constant 42 into address 16)
        binary = pack_instruction(2, 16, 42)
        
        with open(self.binary_file, 'wb') as f:
            f.write(binary)
        
        self.interpreter.run(self.binary_file)
        self.assertEqual(self.interpreter.memory[16], 42)

    def test_write_instruction(self):
        """Test WRITE instruction execution"""
        # First LOAD 16 42, then WRITE 16 32
        binary = pack_instruction(2, 16, 42) + pack_instruction(3, 16, 32)
        
        with open(self.binary_file, 'wb') as f:
            f.write(binary)
        
        self.interpreter.run(self.binary_file)
        self.assertEqual(self.interpreter.memory[32], 42)

    def test_read_instruction(self):
        """Test READ instruction execution"""
        # LOAD 32 42, then READ 16 32
        binary = pack_instruction(2, 32, 42) + pack_instruction(4, 16, 32)
        
        with open(self.binary_file, 'wb') as f:
            f.write(binary)
        
        self.interpreter.run(self.binary_file)
        self.assertEqual(self.interpreter.memory[16], 42)

    def test_le_instruction(self):
        """Test LE instruction execution"""
        # LOAD 16 42
        # LOAD 32 24
        # LE 8 16 32 (Compare values at 16 and 32, store in 8)
        binary = (pack_instruction(2, 16, 42) + 
                 pack_instruction(2, 32, 24) + 
                 pack_instruction(6, 8, 16, 32))
        
        with open(self.binary_file, 'wb') as f:
            f.write(binary)
        
        self.interpreter.run(self.binary_file)
        self.assertEqual(self.interpreter.memory[8], 0)  # 42 is not <= 24

    def test_vector_comparison(self):
        """Test vector comparison program"""
        # Program to compare two vectors of length 3
        program = bytearray()
        
        # First vector: [10, 20, 30] at addresses [100, 101, 102]
        for i, value in enumerate([10, 20, 30]):
            program.extend(pack_instruction(2, 100 + i, value))
        
        # Second vector: [15, 25, 35] at addresses [200, 201, 202]
        for i, value in enumerate([15, 25, 35]):
            program.extend(pack_instruction(2, 200 + i, value))
        
        # Compare elements and store results at addresses [300, 301, 302]
        for i in range(3):
            program.extend(pack_instruction(6, 300 + i, 100 + i, 200 + i))
        
        with open(self.binary_file, 'wb') as f:
            f.write(program)
        
        self.interpreter.run(self.binary_file)
        
        # Save results
        self.interpreter.save_memory_range(300, 302, self.output_file)
        
        # Verify results (all should be 1 since first vector <= second vector)
        for i in range(3):
            self.assertEqual(self.interpreter.memory[300 + i], 1)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Try to read from uninitialized memory
        binary = pack_instruction(4, 16, 32)  # READ 16 32 (32 not initialized)
        
        with open(self.binary_file, 'wb') as f:
            f.write(binary)
        
        with self.assertRaises(ValueError):
            self.interpreter.run(self.binary_file)

if __name__ == '__main__':
    unittest.main()
