from dataclasses import dataclass
from enum import Enum, auto
from error import Error, raise_error
from typing import Optional
import re

class TokenType(Enum):
    ASSIGNMENT = auto()
    BLOCK_END = auto()
    BLOCK_START = auto()
    COMMA = auto()
    COMMENT = auto()
    COMPARE = auto()
    COSTUME = auto()
    EOF = auto()
    FLOAT = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    KEYWORD = auto()
    LEFT_PAREN = auto()
    OPERATOR = auto()
    PREPROCESSING = auto()
    RIGHT_PAREN = auto()
    STATEMENT_END = auto()
    STRING = auto()
    SUBSCRIPT_LEFT = auto()
    SUBSCRIPT_RIGHT = auto()
    WHITE = auto()

TOKEN_REGEX: dict[TokenType, re.Pattern | str] = {
    TokenType.COMMENT: re.compile(r'//[^\n\r]*|/\*.*?\*/', re.DOTALL),
    TokenType.WHITE: r'[ \t\r]+|\\\n',
    TokenType.STATEMENT_END: r';|\n',
    TokenType.LEFT_PAREN: r'\(',
    TokenType.RIGHT_PAREN: r'\)',
    TokenType.BLOCK_START: r'\{',
    TokenType.SUBSCRIPT_LEFT: r'\[',
    TokenType.SUBSCRIPT_RIGHT: r'\]',
    TokenType.BLOCK_END: r'\}',
    TokenType.COMMA: r',',
    TokenType.PREPROCESSING: '#',
    # \u4e00 - \u9fa5 is the unicode range of Chinese characters
    TokenType.IDENTIFIER: r'[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*',
    TokenType.FLOAT: r'[1-9]\d*\.\d*|0?\.\d+',
    TokenType.INTEGER: r'0b[0-1]+|0o[0-7]+|0x[0-9a-fA-F]+|[1-9]\d*|0',
    TokenType.STRING: r'".*?"',
    TokenType.COMPARE: r'==|!=|<=|>=|<|>',
    TokenType.ASSIGNMENT: r'=|\+=|-=|\*=|/=|%=',
    TokenType.OPERATOR: r'->|[+\-*/%]|\.{2}|!|\|\||&&',
}
# Change the string to regex pattern
TOKEN_REGEX = {
    token_type: re.compile(pattern)
                    if isinstance(pattern, str)
                    else pattern
    for token_type, pattern in TOKEN_REGEX.items()
}

@dataclass
class Token:
    type: TokenType
    value: str
    lineno: Optional[int] = None
    

    @property
    def desc(self):
        escaped = self.value.replace('\n', '\\n')
        if self.lineno is None:
            return escaped
        return f'{escaped} (line {self.lineno})'

def tokenize(code: str) -> list[Token]:
    tokens = []
    match: Optional[re.Match] = None
    lineno = 1
    while code:
        for token_type, pattern in TOKEN_REGEX.items():
            match = re.match(pattern, code)
            if not match:
                continue
            code = code[match.end():]
            value = match.group()
            old_lineno = lineno
            lineno += value.count('\n')
            if token_type == TokenType.COMMENT:
                break
            if token_type == TokenType.WHITE:
                break
            if token_type == TokenType.STRING:
                value = value[1:-1]  # Remove the quotes
            if token_type == TokenType.IDENTIFIER:
                if value in ['in', 'contains']:
                    token_type = TokenType.COMPARE
                elif value in ['const', 'var', 'if', 'else', 'while', 'until',
                               'true', 'false', 'function', 'clone', 'array',
                               'delete', 'for', 'attribute']:
                    token_type = TokenType.KEYWORD
            tokens.append(Token(token_type, value, old_lineno))
            break
        if not match:
            raise_error(Error('Tokenize', f'Invalid or unexpected token on "{code[:5]}"'))
    tokens.append(Token(TokenType.STATEMENT_END, 'end of file'))
    tokens.append(Token(TokenType.EOF, 'end of file'))
    return tokens
