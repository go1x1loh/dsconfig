import struct
import csv
import sys

def interpret(binary_file, result_file, memory_range):
    memory = [0] * 1024  # Предположим, что память имеет размер 1024 байта

    with open(binary_file, 'rb') as f:
        binary_data = f.read()

    i = 0
    while i < len(binary_data):
        opcode = binary_data[i]
        if opcode == 6:  # LE
            addresses = struct.unpack('>III', binary_data[i+1:i+13])
            memory[addresses[0]] = int(memory[addresses[1]] <= memory[addresses[2]])
            i += 13
        else:
            addresses = struct.unpack('>II', binary_data[i+1:i+9])
            if opcode == 2:  # LOAD
                memory[addresses[0]] = addresses[1]
            elif opcode == 4:  # READ
                memory[addresses[0]] = memory[memory[addresses[1]]]
            elif opcode == 3:  # WRITE
                memory[addresses[1]] = memory[addresses[0]]
            i += 11

    with open(result_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Address', 'Value'])
        for addr in range(memory_range[0], memory_range[1]):
            writer.writerow([addr, memory[addr]])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: interpreter.py <binary_file> <result_file> <memory_range>")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    memory_range = list(map(int, sys.argv[3].split('-')))

    interpret(binary_file, result_file, memory_range)

