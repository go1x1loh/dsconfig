import csv
from typing import List, Tuple, Optional

class Interpreter:
    def __init__(self):
        self.memory = {}  # Using a dict as sparse memory
        
    def unpack_instruction(self, bytes_data: bytes) -> Tuple[int, int, int, int]:
        """Unpack 11-byte instruction into opcode and operands"""
        if len(bytes_data) != 11:
            raise ValueError("Invalid instruction length")
            
        # Convert bytes to integer
        packed = int.from_bytes(bytes_data, byteorder='little')
        
        # Extract fields
        opcode = packed & 0x7  # First 3 bits
        b = (packed >> 3) & 0xFFFFFFF  # Next 28 bits
        
        if opcode == 6:  # LE operation
            c = (packed >> 31) & 0xFFFFFFF  # Next 28 bits
            d = (packed >> 59) & 0xFFFFFFF  # Final 28 bits
            return opcode, b, c, d
        elif opcode == 2:  # LOAD operation
            c = (packed >> 31) & 0xFFFF  # Next 16 bits
            return opcode, b, c, None
        else:  # READ/WRITE operations
            c = (packed >> 31) & 0xFFFFFFF  # Next 28 bits
            return opcode, b, c, None

    def execute_instruction(self, opcode: int, b: int, c: int, d: Optional[int] = None):
        """Execute a single instruction"""
        if opcode == 2:  # LOAD constant
            self.memory[b] = c
        elif opcode == 3:  # WRITE to memory
            self.memory[c] = self.memory.get(b, 0)
        elif opcode == 4:  # READ from memory
            addr = self.memory.get(c, 0)
            self.memory[b] = self.memory.get(addr, 0)
        elif opcode == 6:  # LE operation
            if d is None:
                raise ValueError("LE operation requires d operand")
            val1 = self.memory.get(c, 0)
            val2 = self.memory.get(d, 0)
            self.memory[b] = 1 if val1 <= val2 else 0
        else:
            raise ValueError(f"Unknown opcode: {opcode}")

    def run(self, input_file: str, output_file: str, start_addr: int, end_addr: int):
        """Run the program and save results"""
        # Read and execute program
        with open(input_file, 'rb') as f:
            while True:
                instruction = f.read(11)
                if not instruction or len(instruction) < 11:
                    break
                opcode, b, c, d = self.unpack_instruction(instruction)
                self.execute_instruction(opcode, b, c, d)

        # Write results
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['address', 'value'])
            for addr in range(start_addr, end_addr + 1):
                writer.writerow([addr, self.memory.get(addr, 0)])
