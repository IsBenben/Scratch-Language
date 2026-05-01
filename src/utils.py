# *-* encoding: utf-8 *-*
"""
Copyright (c) Copyright 2024 Scratch-Language Developers
https://github.com/IsBenben/Scratch-Language
License under the Apache License, version 2.0
"""

from typing import Any
import argparse

valid_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$'
target_ids: dict[Any, str] = {}
current_id = 0

def to_string(number: int) -> str:
    res = ''
    while number > 0:
        res = valid_chars[number % len(valid_chars)] + res
        number //= len(valid_chars)
    return res or '0'

def generate_id(target: Any) -> str:
    global current_id
    if target not in target_ids:
        target_ids[target] = to_string(current_id)
        current_id += 1
    return '__scl_' + target_ids[target]
    # return str(target)  # For debugging

arg_parser = argparse.ArgumentParser(description='Scratch-Language Command Line')
arg_parser.add_argument('--recursionlimit', '-rl', help='Python递归的上限', default=2000, type=int)
arg_parser.add_argument('--quite', '-q', help='静默模式，不会向控制台输出无用内容', action='store_true')
arg_parser.add_argument('--nooptimize', '-no', help='取消优化，用于调试某些特殊情况', action='store_true')

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
mode_group.add_argument('--lint', '-l', help='进行语法分析（适用于自动化的语法高亮程序）', action='store_true')

args = None

def get_args() -> argparse.Namespace:
    global args
    if args is None:
        args = arg_parser.parse_args()
    return args
