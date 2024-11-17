"""
Example usage:
& python cmdnew.py --infile test.scl --sb3 --outfile output.sb3
"""

from error import ScratchLanguageError
from interpret import Interpreter
from parse import Parser
from preprocessing import preprocess
from utils import get_args, arg_parser
import atexit
import json
import sys
import zipfile
import shutil
import os
import time

args = get_args()

if args.lint:
    arg_parser.error('Linter is not implemented yet.')

if not args.quite:
    print('[Scratch-Language] version 1.2.2')
    print()
    start = time.time()
    atexit.register(lambda: print(f'Successfully completed with {time.time() - start:.2f} seconds.'))

folder = os.path.dirname(__file__)
parser = Parser()
interpreter = Interpreter()

if args.recursionlimit <= 10:
    arg_parser.error('递归的上限数字太小')
sys.setrecursionlimit(args.recursionlimit)

infile = None
incode = args.incode
if args.infile is not None:
    infile =  open(args.infile, 'r', encoding='utf-8')
    atexit.register(infile.close)
    incode = infile.read()
outfile = sys.stdout
if args.outfile:
    outfile = open(args.outfile, 'w', encoding='utf-8')
    atexit.register(outfile.close)

# Process the input code
try:
    if args.json:
        interpreter.visit(parser.parse(preprocess(incode)))
        json.dump(interpreter.project, outfile, indent=2)
    elif args.ast:
        outfile.write(parser.parse(preprocess(incode)).dump())
    elif args.sb3:
        if outfile == sys.stdout:
            arg_parser.error('二进制文件不能输出到标准输出')
        interpreter.visit(parser.parse(preprocess(incode)))
        shutil.copyfile(os.path.join(folder, 'default.zip'), outfile.name)
        with zipfile.ZipFile(outfile.name, 'a') as f:
            f.writestr('project.json', json.dumps(interpreter.project, separators=(',', ':')))
    elif args.tokens:
        for token in preprocess(incode):
            outfile.write(token.desc + '\n')
except ScratchLanguageError:
    print('生成时发生错误，请检查您的代码。')
    # raise  # For debugging
