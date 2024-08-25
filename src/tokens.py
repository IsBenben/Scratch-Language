from enum import Enum, auto
from dataclasses import dataclass
import re
from typing import Optional
from error import Error, raise_error

class TokenType(Enum):
    ASSIGNMENT = auto()
    BINARY_OPERATOR = auto()
    BLOCK_END = auto()
    BLOCK_START = auto()
    COMMA = auto()
    COMMENT = auto()
    COMPARE = auto()
    EOF = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    LEFT_PAREN = auto()
    NUMBER = auto()
    RIGHT_PAREN = auto()
    SEMICOLON = auto()
    STRING = auto()
    WHITE = auto()

TOKEN_REGEX: dict[TokenType, re.Pattern | str] = {
    TokenType.COMMENT: re.compile(r'//[^\n\r]*|/\*.*?\*/', re.DOTALL),
    TokenType.WHITE: r'[ \t\n\r]+',
    TokenType.KEYWORD: r'if|else|function|with',
    TokenType.SEMICOLON: r'[;]',
    TokenType.LEFT_PAREN: r'\(',
    TokenType.RIGHT_PAREN: r'\)',
    TokenType.BLOCK_START: r'\{',
    TokenType.BLOCK_END: r'\}',
    TokenType.COMMA: r',',
    TokenType.NUMBER: r'[【1-9]\d*|0',
    TokenType.STRING: r'".*?"',
    TokenType.IDENTIFIER: r'[a-zA-Z_][a-zA-Z0-9_]*',
    TokenType.ASSIGNMENT: r'=|+=|-=|\*=|/=|%=',
    TokenType.BINARY_OPERATOR: r'[+\-*/%]',
    TokenType.COMPARE: r'==|!=|<|>|<=|>='
}
TOKEN_REGEX = {token_type: re.compile(pattern) if isinstance(pattern, str) else pattern for token_type, pattern in TOKEN_REGEX.items()}

@dataclass
class Token:
    type: TokenType
    value: str

def tokenize(code: str) -> list[Token]:
    tokens = []
    match: Optional[re.Match] = None
    while code:
        for token_type, pattern in TOKEN_REGEX.items():
            match = re.match(pattern, code)
            if not match:
                continue
            code = code[match.end():]
            if token_type == TokenType.WHITE or token_type == TokenType.COMMENT:
                break
            value = match.group()
            if token_type == token_type.STRING:
                value = value[1:-1]
            tokens.append(Token(token_type, value))
            break
        if not match:
            raise_error(Error('Tokenize', 'Invalid or unexpected token on "{}".'.format(code[:5])))
    tokens.append(Token(TokenType.EOF, 'end of file'))
    return tokens