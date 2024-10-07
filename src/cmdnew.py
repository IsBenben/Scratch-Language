"""
Example usage:
& python cmdnew.py --infile test.scl --outfile output.sb3 --sb3
"""

from error import ScratchLanguageError
from interpret import Interpreter
from parse import Parser
from tokens import tokenize
import json
import sys
import argparse
import zipfile
import shutil
import os

sys.setrecursionlimit(2000)

folder = os.path.dirname(__file__)
parser = Parser()
interpreter = Interpreter()

print('[Scratch.py] version 1.0')
print()

arg_parser = argparse.ArgumentParser(description='Scratch.py')

in_group = arg_parser.add_mutually_exclusive_group(required=True)
in_group.add_argument('--infile', '-if', help='要解析的文件')
in_group.add_argument('--incode', '-ic', help='要解析的代码')

out_group = arg_parser.add_mutually_exclusive_group(required=True)
out_group.add_argument('--outfile', '-of', help='输出结果到文件')
out_group.add_argument('--outstd', '-os', help='输出结果到标准输出', action='store_true')

mode_group = arg_parser.add_mutually_exclusive_group(required=True)
mode_group.add_argument('--json', '-j', help='输出JSON格式的project文件', action='store_true')
mode_group.add_argument('--ast', '-a', help='输出抽象语法树', action='store_true')
mode_group.add_argument('--sb3', '-s', help='输出打包出的sb3文件', action='store_true')
mode_group.add_argument('--tokens', '-t', help='输出词法分析结果', action='store_true')

args = arg_parser.parse_args()

infile = None
incode = args.incode
if args.infile is not None:
    infile =  open(args.infile, 'r', encoding='utf-8')
    incode = infile.read()
outfile = sys.stdout
if args.outfile:
    outfile = open(args.outfile, 'w', encoding='utf-8')

# Process the input code
try:
    if args.json:
        interpreter.visit(parser.parse(incode))
        json.dump(interpreter.project, outfile, indent=2)
    elif args.ast:
        outfile.write(parser.parse(incode).dump())
    elif args.sb3:
        if outfile == sys.stdout:
            raise TypeError('二进制文件不能输出到标准输出')
        interpreter.visit(parser.parse(incode))
        shutil.copyfile(os.path.join(folder, 'default.zip'), outfile.name)
        with zipfile.ZipFile(outfile.name, 'a') as f:
            f.writestr('project.json', json.dumps(interpreter.project, separators=(',', ':')))
    elif args.tokens:
        for token in tokenize(incode):
            outfile.write(token.desc + '\n')
except ScratchLanguageError:
    print('生成时发生错误，请检查您的代码。')
    # raise  # For debugging

if infile:
    infile.close()
if outfile != sys.stdout:
    outfile.close()
