from typing import Any
import argparse

valid_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$'
target_ids: dict[int, Any] = {}

def generate_id(target: Any) -> str:
    id_num = hash(target) + 9223372036854775809
    while id_num in target_ids and target_ids[id_num] != target:
        id_num += 1
    res = ''
    while id_num > 0:
        res = valid_chars[id_num % len(valid_chars)] + res
        id_num //= len(valid_chars)
    target_ids[id_num] = target
    return '$' + res.zfill(11)
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
