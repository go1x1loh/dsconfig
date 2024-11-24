import struct
import csv
import re
from typing import List, Optional

class Assembler:
    def __init__(self):
        self.opcodes = {
            'LOAD': 2,  # Load constant
            'WRITE': 3, # Write to memory
            'READ': 4,  # Read from memory
            'LE': 6,    # Less than or equal
        }
        
    def pack_instruction(self, opcode: int, b: int, c: int, d: Optional[int] = None) -> List[int]:
        """Pack instruction into 11-byte format according to specification"""
        if opcode == 6:  # LE operation needs 4 fields
            if d is None:
                raise ValueError("LE operation requires 4 fields (opcode, dest, op1, op2)")
            # Pack as: 3 bits opcode, 28 bits B, 28 bits C, 28 bits D
            packed = (opcode & 0x7) | ((b & 0xFFFFFFF) << 3) | \
                    ((c & 0xFFFFFFF) << 31) | ((d & 0xFFFFFFF) << 59)
        else:
            # Pack as: 3 bits opcode, 28 bits B, 16/28 bits C
            packed = (opcode & 0x7) | ((b & 0xFFFFFFF) << 3)
            if opcode == 2:  # LOAD uses 16-bit constant
                packed |= ((c & 0xFFFF) << 31)
            else:  # Other operations use 28-bit address
                packed |= ((c & 0xFFFFFFF) << 31)

        # Convert to 11 bytes
        result = []
        for i in range(11):
            result.append((packed >> (i * 8)) & 0xFF)
        return result

    def parse_line(self, line: str) -> tuple:
        """Parse a single line of assembly code"""
        line = line.strip()
        if not line or line.startswith(';'):
            return None
            
        # Remove comments
        line = line.split(';')[0].strip()
        
        # Split into tokens
        tokens = re.split(r'[,\s]+', line)
        tokens = [t for t in tokens if t]
        
        if not tokens:
            return None
            
        opcode = tokens[0].upper()
        if opcode not in self.opcodes:
            raise ValueError(f"Unknown opcode: {opcode}")
            
        # Parse operands
        operands = [int(t) for t in tokens[1:]]
        return (self.opcodes[opcode], *operands)

    def assemble(self, input_file: str, output_file: str, log_file: str):
        """Assemble the input file into binary and generate log"""
        with open(input_file, 'r') as f, \
             open(output_file, 'wb') as out, \
             open(log_file, 'w', newline='') as log:
            
            csv_writer = csv.writer(log)
            csv_writer.writerow(['instruction', 'bytes'])
            
            for line_num, line in enumerate(f, 1):
                parsed = self.parse_line(line)
                if parsed is None:
                    continue
                    
                try:
                    packed = self.pack_instruction(*parsed)
                    # Write binary
                    out.write(bytes(packed))
                    # Write log
                    hex_bytes = [f"0x{b:02X}" for b in packed]
                    csv_writer.writerow([line.strip(), ", ".join(hex_bytes)])
                except Exception as e:
                    raise ValueError(f"Error on line {line_num}: {str(e)}")
