import unittest
from assembler import Assembler
from interpreter import Interpreter
import os

class TestMachine(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler()
        self.interpreter = Interpreter()

    def test_load_constant(self):
        """Test for loading constant instruction (A=2)"""
        expected = [0xB2, 0x0A, 0x00, 0x00, 0x83, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        result = self.assembler.pack_instruction(2, 342, 262)
        self.assertEqual(result, expected)

    def test_read_memory(self):
        """Test for reading memory instruction (A=4)"""
        expected = [0xBC, 0x08, 0x00, 0x00, 0x1D, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
        result = self.assembler.pack_instruction(4, 279, 570)
        self.assertEqual(result, expected)

    def test_write_memory(self):
        """Test for writing memory instruction (A=3)"""
        expected = [0xB3, 0x0F, 0x00, 0x80, 0xD3, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
        result = self.assembler.pack_instruction(3, 502, 935)
        self.assertEqual(result, expected)

    def test_less_equal_operation(self):
        """Test for less or equal operation (A=6)"""
        expected = [0x56, 0x1D, 0x00, 0x80, 0x37, 0x00, 0x00, 0x28, 0x15, 0x00, 0x00]
        result = self.assembler.pack_instruction(6, 938, 111, 677)
        self.assertEqual(result, expected)

    def test_vector_comparison(self):
        """Test program that performs element-wise <= operation on two vectors of length 7"""
        # Create test program in assembly
        program = """
        ; Initialize first vector at address 100
        LOAD 100, 5    ; v1[0]
        LOAD 101, 8    ; v1[1]
        LOAD 102, 2    ; v1[2]
        LOAD 103, 9    ; v1[3]
        LOAD 104, 1    ; v1[4]
        LOAD 105, 7    ; v1[5]
        LOAD 106, 3    ; v1[6]

        ; Initialize second vector at address 200
        LOAD 200, 6    ; v2[0]
        LOAD 201, 4    ; v2[1]
        LOAD 202, 3    ; v2[2]
        LOAD 203, 8    ; v2[3]
        LOAD 204, 2    ; v2[4]
        LOAD 205, 7    ; v2[5]
        LOAD 206, 1    ; v2[6]

        ; Perform element-wise comparison
        LE 200, 100, 200  ; v2[0] = v1[0] <= v2[0]
        LE 201, 101, 201  ; v2[1] = v1[1] <= v2[1]
        LE 202, 102, 202  ; v2[2] = v1[2] <= v2[2]
        LE 203, 103, 203  ; v2[3] = v1[3] <= v2[3]
        LE 204, 104, 204  ; v2[4] = v1[4] <= v2[4]
        LE 205, 105, 205  ; v2[5] = v1[5] <= v2[5]
        LE 206, 106, 206  ; v2[6] = v1[6] <= v2[6]
        """
        
        # Write program to temporary file
        with open("test_program.asm", "w") as f:
            f.write(program)

        # Assemble and run
        self.assembler.assemble("test_program.asm", "test_program.bin", "test_program.log")
        self.interpreter.run("test_program.bin", "result.csv", 200, 206)

        # Read results and verify
        with open("result.csv", "r") as f:
            next(f)  # Skip header row
            results = [int(line.strip().split(",")[1]) for line in f]

        expected = [1, 0, 1, 0, 1, 1, 0]  # Expected results after comparison
        self.assertEqual(results, expected)

        # Cleanup
        os.remove("test_program.asm")
        os.remove("test_program.bin")
        os.remove("test_program.log")
        os.remove("result.csv")

if __name__ == '__main__':
    unittest.main()
