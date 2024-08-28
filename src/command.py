from parse import Parser
from tokens import tokenize
from interpret import Interpreter
import json

def run_cmd():
    parser = Parser()
    interpreter = Interpreter()

    print('[Scratch.py] Alpha 0.1')
    print('[Scratch.py] Welcome to the CMD. Type "help" for help.')
    print()

    while True:
        user_input = input('~ ')
        
        if user_input == 'exit':
            print('[Scratch.py] Exited.')
            break
        elif user_input == 'help':
            print('[Scratch.py] Available commands: exit, tokenize, parse, file, save')
        elif user_input == 'tokenize':
            code = input('[Scratch.py] Enter code: ')
            for token in tokenize(code):
                print(repr(token))
        elif user_input == 'parse':
            code = input('[Scratch.py] Enter code: ')
            print(parser.parse(code).dump().replace('\n', '\n'))
        elif user_input == 'file':
            interpreter = Interpreter()
            code = input('[Scratch.py] Enter filename: ')
            with open(code, 'r', encoding='utf-8') as f:
                user_input = f.read()
            interpreter.visit(parser.parse(user_input))
        elif user_input == 'save':
            outfile = input('[Scratch.py] Enter filename: ')
            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(json.dumps(interpreter.project, separators=(',', ':')))
        else:
            print('[Scratch.py] Unknown command.')
        print()

if __name__ == '__main__':
    run_cmd()
