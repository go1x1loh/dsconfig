import unittest
import os
import tempfile
from assembler import assemble, pack_instruction

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, 'input.txt')
        self.output_file = os.path.join(self.test_dir, 'output.bin')
        self.log_file = os.path.join(self.test_dir, 'log.csv')

    def test_load_instruction(self):
        """Test LOAD instruction encoding (A=2, B=342, C=262)"""
        expected = [0xB2, 0x0A, 0x00, 0x00, 0x83, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        binary = pack_instruction(2, 342, 262)
        self.assertEqual(binary, expected)

    def test_write_instruction(self):
        """Test WRITE instruction encoding (A=3, B=502, C=935)"""
        expected = [0xB3, 0x0F, 0x00, 0x80, 0xD3, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
        binary = pack_instruction(3, 502, 935)
        self.assertEqual(binary, expected)

    def test_read_instruction(self):
        """Test READ instruction encoding (A=4, B=279, C=570)"""
        expected = [0xBC, 0x08, 0x00, 0x00, 0x1D, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
        binary = pack_instruction(4, 279, 570)
        self.assertEqual(binary, expected)

    def test_le_instruction(self):
        """Test LE instruction encoding (A=6, B=938, C=111, D=677)"""
        expected = [0x56, 0x1D, 0x00, 0x80, 0x37, 0x00, 0x00, 0x28, 0x15, 0x00, 0x00]
        binary = pack_instruction(6, 938, 111, 677)
        self.assertEqual(binary, expected)

    def test_vector_comparison_program(self):
        """Test vector comparison program that performs element-wise <= operation"""
        # Create test program that compares two vectors of length 7
        program = """
        # Initialize first vector at address 100
        LOAD 100 5   # v1[0]
        LOAD 101 12  # v1[1]
        LOAD 102 8   # v1[2]
        LOAD 103 15  # v1[3]
        LOAD 104 3   # v1[4]
        LOAD 105 9   # v1[5]
        LOAD 106 1   # v1[6]

        # Initialize second vector at address 200
        LOAD 200 6   # v2[0]
        LOAD 201 10  # v2[1]
        LOAD 202 8   # v2[2]
        LOAD 203 20  # v2[3]
        LOAD 204 2   # v2[4]
        LOAD 205 11  # v2[5]
        LOAD 206 0   # v2[6]

        # Perform element-wise comparison and store results in second vector
        LE 200 100 200  # v2[0] = v1[0] <= v2[0]
        LE 201 101 201  # v2[1] = v1[1] <= v2[1]
        LE 202 102 202  # v2[2] = v1[2] <= v2[2]
        LE 203 103 203  # v2[3] = v1[3] <= v2[3]
        LE 204 104 204  # v2[4] = v1[4] <= v2[4]
        LE 205 105 205  # v2[5] = v1[5] <= v2[5]
        LE 206 106 206  # v2[6] = v1[6] <= v2[6]
        """

        # Write test program
        with open(self.input_file, 'w') as f:
            f.write(program)

        # Assemble program
        assemble(self.input_file, self.output_file, self.log_file)

        # Verify binary output exists and has correct size
        with open(self.output_file, 'rb') as f:
            binary = f.read()
            # 21 instructions total (7 for first vector + 7 for second vector + 7 comparisons)
            # Each instruction is 11 bytes
            self.assertEqual(len(binary), 21 * 11)

        # Verify log file exists and contains the correct number of instructions
        with open(self.log_file, 'r') as f:
            log_lines = f.readlines()
            # Header line + 21 instructions
            self.assertEqual(len(log_lines), 22)

    def test_full_assembly(self):
        """Test full assembly process with multiple instructions"""
        # Write test program
        with open(self.input_file, 'w') as f:
            f.write("LOAD 16 42\n")  # Load 42 into address 16
            f.write("WRITE 16 32\n") # Write from 16 to 32
            f.write("READ 48 32\n")  # Read from 32 to 48
            f.write("LE 8 48 16\n")  # Compare 48 and 16, store in 8

        # Assemble program
        assemble(self.input_file, self.output_file, self.log_file)

        # Verify binary output
        with open(self.output_file, 'rb') as f:
            binary = f.read()

        # Each instruction should be 11 bytes
        self.assertEqual(len(binary), 44)  # 4 instructions * 11 bytes

        # Verify first instruction (LOAD)
        self.assertEqual(binary[0], 0xB2)  # opcode 2
        self.assertEqual(binary[1], 0x01)  # address 16 >> 4
        self.assertEqual(binary[4], 42)    # constant 42

        # Verify second instruction (WRITE)
        self.assertEqual(binary[11], 0xB3) # opcode 3
        self.assertEqual(binary[12], 0x01) # address 16 >> 4
        self.assertEqual(binary[14], 0x80) # special case for WRITE
        self.assertEqual(binary[15], 32)   # address 32

        # Verify third instruction (READ)
        self.assertEqual(binary[22], 0xB4) # opcode 4
        self.assertEqual(binary[23], 0x03) # address 48 >> 4
        self.assertEqual(binary[26], 32)   # address 32

        # Verify fourth instruction (LE)
        self.assertEqual(binary[33], 0x56) # special case for LE
        self.assertEqual(binary[34], 0x00) # address 8 >> 4
        self.assertEqual(binary[37], 48)   # first comparison address
        self.assertEqual(binary[41], 16)   # second comparison address

if __name__ == '__main__':
    unittest.main()
