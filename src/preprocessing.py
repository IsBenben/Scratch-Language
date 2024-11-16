from dataclasses import dataclass
from tokens import Token, TokenType, tokenize
from error import Error, raise_error
import os

HEADER_PATH = os.path.join(os.path.dirname(__file__), '../includes')

@dataclass
class Define:
    tokens: list[Token]
    params: list[str] | None = None

def preprocess(tokens: str | list[Token], relative_path: str = os.getcwd()) -> list[Token]:
    if isinstance(tokens, str):
        tokens = tokenize(tokens)

    def list_split(seq: list[Token]) -> list[list[Token]]:
        if not seq:
            return []
        result = []
        lineno = 0
        for ele in seq:
            if ele.lineno != lineno:
                result.append([])
                lineno = ele.lineno
            assert len(result) > 0 and isinstance(result[-1], list)
            result[-1].append(ele)
        return result
    
    def list_find_from_back(seq: list[Token], token_type: TokenType) -> tuple[int, Token] | tuple[None, None]:
        for i, ele in reversed(list(enumerate(seq))):
            if ele.type == token_type:
                return i, ele
        return None, None

    # Unfold all preprocessing directives
    
    lines = list_split(tokens)
    defines: dict[str, dict[int, Define]] = {}  # "str" means name, "int" means params count
    for i, line in enumerate(lines):
        if not line:
            continue
        if line[0].type == TokenType.PREPROCESSING:
            if line[-1].type != TokenType.STATEMENT_END:
                raise_error(Error('Preprocessing', f'Unexpected token "{line[-1].desc}", expected {TokenType.STATEMENT_END}'))
            line.pop()
            if len(line) < 2 or line[1].type != TokenType.IDENTIFIER:
                raise_error(Error('Preprocessing', f'Directive name after "{line[0].desc}" is not found'))
            if line[1].value == 'include':
                path = ''
                if len(line) == 3 \
                       and line[2].type == TokenType.STRING:
                    #include "path/to/file"
                    path = os.path.join(relative_path, line[2].value)
                elif len(line) == 5 \
                         and line[2].type == TokenType.COMPARE \
                         and line[2].value == '<' \
                         and line[3].type == TokenType.IDENTIFIER \
                         and line[4].type == TokenType.COMPARE \
                         and line[4].value == '>':
                    # #include <header_name>
                    path = os.path.join(HEADER_PATH, line[3].value + '.scl')
                else:
                    raise_error(Error('Preprocessing', f'The syntax of directive "{line[1].desc}" is invalid'))
                
                if not os.path.exists(path):
                    raise_error(Error('Preprocessing', f'File "{path}" does not exist (in directive {line[1].desc})'))
                with open(path, 'r', encoding='utf-8') as f:
                    for line_inner in reversed(list_split(tokenize(f.read())[:-1])):
                        lines.insert(i + 1, line_inner)
            elif line[1].value == 'define':
                def test_3():
                    # Test of "#define value identifier(param1, param2, ...)"
                    # Return the index of left paren, return -1 if the syntax invalid
                    i, _ = list_find_from_back(line, TokenType.LEFT_PAREN)
                    if i is None:
                        return -1
                    # ? What is the compare
                    result = len(line) >= 7 \
                                 and line[-1].type == TokenType.RIGHT_PAREN \
                                 and 4 <= i <= len(line) - 2 \
                                 and all(map(lambda x: x.type == TokenType.COMMA, line[i+2:-1:2])) \
                                 and all(map(lambda x: x.type == TokenType.IDENTIFIER, line[i-1:-1:2]))
                    if result:
                        return i
                    return -1

                name = None
                params = None
                if len(line) >= 4 and line[-1].type == TokenType.IDENTIFIER:
                    # #define value identifier
                    name = -1
                elif len(line) >= 6 \
                         and line[-1].type == TokenType.RIGHT_PAREN \
                         and line[-2].type == TokenType.LEFT_PAREN \
                         and line[-3].type == TokenType.IDENTIFIER:
                    # #define value identifier()
                    name = -3
                    params = []
                elif test_3() != -1:
                    # #define value identifier(param1, param2, ...)
                    ret = test_3()
                    name = ret - 1
                    params = list(map(lambda x: x.value, line[ret+1:-1:2]))
                else:
                    raise_error(Error('Preprocessing', f'The syntax of directive "{line[1].desc}" is invalid'))
                
                assert name is not None
                name_str = line[name].value
                defines.setdefault(name_str, {})
                params_count = -1 if params is None else len(params)
                defines[name_str][params_count] = Define(line[2:name], params) 
            elif line[1].value == 'undef':
                # #undef identifier
                if len(line) != 3 or line[2].type != TokenType.IDENTIFIER:
                    raise_error(Error('Preprocessing', f'The syntax of directive "{line[1].desc}" is invalid'))
                if line[2].value not in defines:
                    raise_error(Error('Preprocessing', f'"{line[2].desc}" is not defined (in directive {line[1].desc})'))
                defines.pop(line[2].value)
            elif line[1].value == 'error':
                # #error message
                if len(line) != 3 or line[2].type != TokenType.STRING:
                    raise_error(Error('Preprocessing', f'The syntax of directive "{line[1].desc}" is invalid'))
                raise_error(Error('Preprocessing', f'User error: {line[2].desc}'))
            else:
                raise_error(Error('Preprocessing', f'Unknown directive "{line[1].desc}"'))
            line.clear()
            continue

        for j, token in enumerate(line):
            if token is None:
                continue
            if token.type == TokenType.IDENTIFIER and token.value in defines:
                line[j] = None  # type: ignore
                # Try to find the right paren
                walk_i = i
                walk_j = j
                walk_tokens = [token]
                walk_parens = []
                walk_params: None | list[list[Token]] = None
                while True:
                    walk_j += 1
                    while walk_j >= len(lines[walk_i]):
                        walk_j = 0
                        walk_i += 1
                        if walk_i >= len(lines):
                            if walk_parens:
                                raise_error(Error('Preprocessing', f'Cannot find the right paren of "{line[j + 1].desc}"'))
                            else:
                                break
                    tk = lines[walk_i][walk_j]
                    walk_tokens.append(tk)
                    add_to_params = True
                    set_to_none = True
                    if tk.type == TokenType.LEFT_PAREN:
                        if walk_params is None:
                            walk_params = [[]]
                            add_to_params = False
                        walk_parens.append(tk)
                    elif tk.type == TokenType.RIGHT_PAREN:
                        if walk_parens:
                            walk_parens.pop()
                        else:
                            set_to_none = False
                    elif tk.type == TokenType.COMMA:
                        if walk_parens and len(walk_parens) == 1:
                            # Outer paren
                            assert walk_params is not None
                            walk_params.append([])
                            add_to_params = False
                    
                    if add_to_params:
                        if walk_parens:
                            assert walk_params is not None
                            walk_params[-1].append(tk)
                    if set_to_none:
                        lines[walk_i][walk_j] = None  # type: ignore
                    else:
                        walk_tokens.pop()
                    
                    if not walk_parens:
                        if len(walk_tokens) >= 2:
                            assert walk_params is not None
                            if walk_params == [[]]:
                                assert len(walk_tokens) == 3  # identifier()
                                walk_params.clear()
                        else:
                            assert len(walk_tokens) == 1  # identifier
                            walk_params = None
                            walk_j -= 1  # This program run by this bug
                        break
                    
                params_count = -1 if walk_params is None else len(walk_params)
                overloads = defines[token.value]
                if params_count not in overloads:
                    raise_error(Error('Preprocessing', f'Cannot find {params_count} parameters overload of define "{token.desc}"'))
                for token_inner in reversed(overloads[params_count].tokens):
                    params = overloads[params_count].params
                    if params:
                        assert walk_params
                        if token_inner.type == TokenType.IDENTIFIER and token_inner.value in params:
                            param_index = params.index(token_inner.value)
                            for token_inner_param in reversed(walk_params[param_index]):
                                lines[walk_i].insert(walk_j + 1, token_inner_param)
                            continue
                    lines[walk_i].insert(walk_j + 1, token_inner)
        while None in line:
            line.remove(None)  # type: ignore
    # Flat the list
    result = sum(lines, start=[])
    return result
