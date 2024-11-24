import struct
import csv
import sys

def pack_instruction(opcode, *args):
    """Pack instruction according to UVM specification.
    All instructions are 11 bytes long.
    Bits 0-2: opcode
    Bits 3-30: first address (B)
    Bits 31-58/46: second address (C) or constant
    For LE operation:
    Bits 59-86: third address (D)
    """
    result = bytearray(11)  # All instructions are 11 bytes
    
    # Pack opcode (bits 0-2) and first address B (bits 3-30)
    if opcode == 6:  # LE operation
        result[0] = 0x56  # Special case for LE
    else:
        result[0] = 0xB0 | opcode  # Other operations
    
    # Pack first address B
    addr_b = args[0]
    result[1] = (addr_b >> 4) & 0xFF
    result[2] = 0x00
    result[3] = 0x00 if opcode != 3 else 0x80  # Special case for WRITE
    
    # Pack second value C
    value_c = args[1]
    result[4] = value_c & 0xFF
    result[5] = 0x00
    result[6] = 0x00
    result[7] = 0x00
    
    # Pack third address D for LE operation
    if len(args) >= 3:
        addr_d = args[2]
        result[8] = addr_d & 0xFF
        result[9] = (addr_d >> 8) & 0xFF
        result[10] = 0x00
    else:
        result[8] = 0x00
        result[9] = 0x00
        result[10] = 0x00
    
    return result

def assemble(input_file, output_file, log_file):
    commands = {
        'LOAD': 2,   # Load constant
        'WRITE': 3,  # Write to memory
        'READ': 4,   # Read from memory
        'LE': 6      # Less than or equal
    }

    with open(input_file, 'r') as f:
        lines = f.readlines()

    binary_output = bytearray()
    log_entries = []

    for line in lines:
        # Skip comments and empty lines
        line = line.split('#')[0].strip()
        if not line:
            continue

        parts = line.strip().split()
        command = parts[0]
        addresses = list(map(int, parts[1:]))

        if command not in commands:
            raise ValueError(f"Unknown command: {command}")

        opcode = commands[command]
        
        # Pack the instruction according to the specification
        binary_command = pack_instruction(opcode, *addresses)
        binary_output.extend(binary_command)

        # Create log entry
        log_entry = {
            'command': command,
            'opcode': hex(opcode),
            'addresses': ','.join(map(str, addresses))
        }
        log_entries.append(log_entry)

    # Write binary output
    with open(output_file, 'wb') as f:
        f.write(binary_output)

    # Write log in CSV format
    with open(log_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['command', 'opcode', 'addresses'])
        writer.writeheader()
        writer.writerows(log_entries)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]

    try:
        assemble(input_file, output_file, log_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
