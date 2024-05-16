import sys
from Transpiler import Lexer, Token, TokenTypes, Parser, Emitter

if __name__ == "__main__":
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as input_file:
        input = input_file.read()

    # Initialize the lexer and parser.
    lexer = Lexer(input)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program() # Start the parser.
    emitter.write_file() 
    print("Parsing completed.")