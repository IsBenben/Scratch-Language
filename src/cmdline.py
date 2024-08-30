"""
Example usage:
python cmdline.py -infile test.scl -outfile project.json
"""

from interpret import Interpreter
from parse import Parser
from tokens import tokenize
import json
import sys

sys.setrecursionlimit(2000)

def run_command(args: list[str]):
    parser = Parser()
    interpreter = Interpreter()

    print('[Scratch.py] Alpha 0.1')
    print()

    params = {}
    for i in range(1, len(args)):
        if args[i].startswith('-'):
            params[args[i][1:]] = i
    if params.get('infile'):
        with open(args[params['infile'] + 1], 'r', encoding='utf-8') as f:
            code = f.read()
    elif params.get('incode'):
        code = args[params['incode'] + 1]
    else:
        code = input('>>> ')

    if params.get('outfile'):
        interpreter.visit(parser.parse(code))
        with open(args[params['outfile'] + 1], 'w', encoding='utf-8') as f:
            f.write(json.dumps(interpreter.project, separators=(',', ':')))
    elif params.get('outcode'):
        interpreter.visit(parser.parse(code))
        print(json.dumps(interpreter.project, separators=(',', ':')))
    elif params.get('outtokens'):
        for token in tokenize(code):
            print(token)
    elif params.get('outast'):
        print(parser.parse(code))
    else:
        raise ValueError('Invalid command line arguments')


if __name__ == '__main__':
    run_command(sys.argv)
