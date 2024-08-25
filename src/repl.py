from parse import Parser
from tokens import tokenize
from interpret import Interpreter

def run_repl():
    print('#[Scratch.py] Alpha 0.1')
    parser = Parser()
    interpreter = Interpreter()
    print('#[Scratch.py] Welcome to the REPL. Type ".help" for help.')
    print()

    while True:
        user_input = input('#~ ')
        if user_input.startswith('.'):
            if user_input == '.exit':
                print('#[REPL] Exited.')
                break
            elif user_input == '.help':
                print('#[REPL] Available commands: .exit, .tokenize, .parse, .file')
                continue
            elif user_input == '.tokenize':
                code = input('#[REPL] Enter code: ')
                for token in tokenize(code):
                    print('#' + repr(token))
                continue
            elif user_input == '.parse':
                code = input('#[REPL] Enter code: ')
                print('#' + parser.parse(code).dump().replace('\n', '\n#'))
                continue
            elif user_input == '.file':
                code = input('#[REPL] Enter filename: ')
                with open(code, 'r') as f:
                    user_input = f.read()
            else:
                print('#[REPL] Unknown command.')
                continue
        interpreter.visit(parser.parse(user_input))
        print()

if __name__ == '__main__':
    run_repl()
