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
        """Test LOAD instruction encoding"""
        # LOAD 16 42 (Load constant 42 into address 16)
        binary = pack_instruction(2, 16, 42)
        self.assertEqual(binary[0], 0xB2)  # opcode 2
        self.assertEqual(binary[1], 0x01)  # address 16 >> 4
        self.assertEqual(binary[4], 42)    # constant value 42

    def test_write_instruction(self):
        """Test WRITE instruction encoding"""
        # WRITE 32 64 (Write from address 32 to 64)
        binary = pack_instruction(3, 32, 64)
        self.assertEqual(binary[0], 0xB3)  # opcode 3
        self.assertEqual(binary[1], 0x02)  # address 32 >> 4
        self.assertEqual(binary[3], 0x80)  # special case for WRITE
        self.assertEqual(binary[4], 64)    # address 64

    def test_read_instruction(self):
        """Test READ instruction encoding"""
        # READ 48 96 (Read from address 96 to 48)
        binary = pack_instruction(4, 48, 96)
        self.assertEqual(binary[0], 0xB4)  # opcode 4
        self.assertEqual(binary[1], 0x03)  # address 48 >> 4
        self.assertEqual(binary[4], 96)    # address 96

    def test_le_instruction(self):
        """Test LE instruction encoding"""
        # LE 8 16 32 (Compare values at 16 and 32, store in 8)
        binary = pack_instruction(6, 8, 16, 32)
        self.assertEqual(binary[0], 0x56)  # special case for LE
        self.assertEqual(binary[1], 0x00)  # address 8 >> 4
        self.assertEqual(binary[4], 16)    # first comparison address
        self.assertEqual(binary[8], 32)    # second comparison address
        self.assertEqual(binary[9], 0x00)  # high byte of second address

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
