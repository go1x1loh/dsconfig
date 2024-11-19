import struct
import csv
import sys

def assemble(input_file, output_file, log_file):
    commands = {
        'LOAD': 2,
        'READ': 4,
        'WRITE': 3,
        'LE': 6
    }

    with open(input_file, 'r') as f:
        lines = f.readlines()

    binary_output = bytearray()
    log_entries = []

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue  # Пропускаем пустые строки

        command = parts[0]
        addresses = list(map(int, parts[1:]))

        if command not in commands:
            raise ValueError(f"Unknown command: {command}")

        opcode = commands[command]
        if command == 'LE':
            if len(addresses) != 3:
                raise ValueError(f"Command {command} expects 3 addresses, got {len(addresses)}")
            binary_command = struct.pack('>BIII', opcode, *addresses)
        else:
            if len(addresses) != 2:
                raise ValueError(f"Command {command} expects 2 addresses, got {len(addresses)}")
            binary_command = struct.pack('>BII', opcode, *addresses)

        binary_output.extend(binary_command)

        log_entries.append({
            'command': command,
            'opcode': opcode,
            'addresses': addresses
        })

    with open(output_file, 'wb') as f:
        f.write(binary_output)

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

    assemble(input_file, output_file, log_file)

