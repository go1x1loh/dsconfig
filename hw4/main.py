import argparse
from assembler import Assembler
from interpreter import Interpreter

def main():
    parser = argparse.ArgumentParser(description='Educational Virtual Machine Assembler and Interpreter')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Assembler command
    asm_parser = subparsers.add_parser('assemble', help='Assemble source code')
    asm_parser.add_argument('input', help='Input assembly file')
    asm_parser.add_argument('output', help='Output binary file')
    asm_parser.add_argument('log', help='Log file (CSV format)')
    
    # Interpreter command
    int_parser = subparsers.add_parser('run', help='Run binary program')
    int_parser.add_argument('input', help='Input binary file')
    int_parser.add_argument('output', help='Output results file (CSV format)')
    int_parser.add_argument('start_addr', type=int, help='Start address of memory range to output')
    int_parser.add_argument('end_addr', type=int, help='End address of memory range to output')
    
    args = parser.parse_args()
    
    if args.command == 'assemble':
        assembler = Assembler()
        try:
            assembler.assemble(args.input, args.output, args.log)
            print(f"Successfully assembled {args.input} to {args.output}")
            print(f"Assembly log written to {args.log}")
        except Exception as e:
            print(f"Error during assembly: {str(e)}")
            exit(1)
            
    elif args.command == 'run':
        interpreter = Interpreter()
        try:
            interpreter.run(args.input, args.output, args.start_addr, args.end_addr)
            print(f"Successfully executed {args.input}")
            print(f"Results written to {args.output}")
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            exit(1)
    else:
        parser.print_help()
        exit(1)

if __name__ == '__main__':
    main()
