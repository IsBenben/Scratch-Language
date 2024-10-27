"""
Example usage:
& python cmdnew.py --infile test.scl --sb3 --outfile output.sb3
"""

from error import ScratchLanguageError
from interpret import Interpreter
from parse import Parser
from preprocessing import preprocess
import json
import sys
import argparse
import zipfile
import shutil
import os

folder = os.path.dirname(__file__)
parser = Parser()
interpreter = Interpreter()

print('[Scratch-Language] version 1.1')
print()

arg_parser = argparse.ArgumentParser(description='Scratch-Language Command Line')
arg_parser.add_argument('--recursionlimit', '-rl', help='Python递归的上限', default='2000')

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

if not args.recursionlimit.isdigit():
    arg_parser.error('递归的上限不是整数')
if int(args.recursionlimit) <= 10:
    arg_parser.error('递归的上限数字太小')
else:
    sys.setrecursionlimit(int(args.recursionlimit))

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

if infile:
    infile.close()
if outfile != sys.stdout:
    outfile.close()
