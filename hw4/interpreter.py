import struct
import csv
import sys

class UVMInterpreter:
    def __init__(self):
        self.memory = {}  # Virtual memory space
        self.instruction_size = 11  # All instructions are 11 bytes

    def unpack_instruction(self, binary_data, offset):
        """Unpack a single instruction from binary data at given offset.
        Returns tuple (opcode, addresses) following UVM specification.
        """
        if len(binary_data) < offset + self.instruction_size:
            raise ValueError("Incomplete instruction")

        instruction = binary_data[offset:offset + self.instruction_size]
        
        # Extract opcode (bits 0-2)
        if instruction[0] == 0x56:  # Special case for LE
            opcode = 6
        else:
            opcode = instruction[0] & 0x0F
        
        # Extract first address B (bits 3-30)
        addr_b = (instruction[1] << 4) & 0xFF
        
        if opcode == 2:  # LOAD
            value = instruction[4] & 0xFF  # For LOAD, second parameter is a value
            return opcode, [addr_b, value]
        elif opcode == 6:  # LE
            addr_c = instruction[4] & 0xFF  # Second address
            addr_d = instruction[8] & 0xFF  # Third address
            return opcode, [addr_b, addr_c, addr_d]
        else:  # READ or WRITE
            addr_c = instruction[4] & 0xFF  # Second address
            return opcode, [addr_b, addr_c]

    def execute_instruction(self, opcode, addresses):
        """Execute a single UVM instruction"""
        if opcode == 2:  # LOAD
            addr_b, value = addresses
            self.memory[addr_b] = value
            print(f"LOAD: Storing value {value} at address {addr_b}")
        elif opcode == 3:  # WRITE
            addr_b, addr_c = addresses
            if addr_b not in self.memory:
                raise ValueError(f"Memory location {addr_b} not initialized")
            self.memory[addr_c] = self.memory[addr_b]
            print(f"WRITE: Copying value {self.memory[addr_b]} from address {addr_b} to {addr_c}")
        elif opcode == 4:  # READ
            addr_b, addr_c = addresses
            if addr_c not in self.memory:
                raise ValueError(f"Memory location {addr_c} not initialized")
            self.memory[addr_b] = self.memory[addr_c]
            print(f"READ: Reading value {self.memory[addr_c]} from address {addr_c} to {addr_b}")
        elif opcode == 6:  # LE
            addr_b, addr_c, addr_d = addresses
            # Compare values and store result
            value_c = self.memory.get(addr_c, 0)
            value_d = self.memory.get(addr_d, 0)
            result = 1 if value_c <= value_d else 0
            self.memory[addr_b] = result
            print(f"LE: Comparing {value_c} (<= {addr_c}) with {value_d} (<= {addr_d}), storing {result} at {addr_b}")
        else:
            raise ValueError(f"Unknown opcode: {opcode}")

    def run(self, binary_file):
        """Execute all instructions from binary file"""
        with open(binary_file, 'rb') as f:
            binary_data = f.read()

        offset = 0
        while offset < len(binary_data):
            opcode, addresses = self.unpack_instruction(binary_data, offset)
            self.execute_instruction(opcode, addresses)
            offset += self.instruction_size

    def save_memory_range(self, start_addr, end_addr, output_file):
        """Save memory contents within given range to CSV file"""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Value'])
            for addr in range(start_addr, end_addr + 1):
                value = self.memory.get(addr, 0)  # Default to 0 for uninitialized memory
                writer.writerow([addr, value])

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: interpreter.py <binary_file> <output_file> <start_addr> <end_addr>")
        sys.exit(1)

    binary_file = sys.argv[1]
    output_file = sys.argv[2]
    start_addr = int(sys.argv[3])
    end_addr = int(sys.argv[4])

    try:
        interpreter = UVMInterpreter()
        interpreter.run(binary_file)
        interpreter.save_memory_range(start_addr, end_addr, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
