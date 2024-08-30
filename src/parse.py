from tokens import TokenType, tokenize, Token
from nodes import *
from error import Error, raise_error
from typing import Optional, NoReturn, Any, Callable

sign_to_english = {
    '+': 'add',
    '-': 'subtract',
    '*': 'multiply',
    '/': 'divide',
    '%': 'mod',
    '>': 'gt',
    '<': 'lt',
    '==': 'equals',
    '!': 'not',
    '||': 'or',
    '&&': 'and',
    '..': 'join',
}
inverse_sign = {
    '!=': '==',
    '<': '>=',
    '<=': '>',
    '==': '!=',
    '>': '<=',
    '>=': '<',
}

def extend_or_append(list_: list, value: list | Any):
    if isinstance(value, list):
        list_.extend(value)
    else:
        list_.append(value)
    return list_

class Parser:
    def parse(self, code: str) -> Program:
        return self.parse_program(tokenize(code))
    
    def eat(self, tokens: list[Token], type: Optional[TokenType]=None) -> Token:
        if type is None:
            return tokens.pop(0)
        if tokens[0].type == type:
            return tokens.pop(0)
        raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected {type}'))

    def parse_program(self, tokens: list[Token]) -> Program:
        program = Program()
        while tokens[0].type != TokenType.EOF:
            statement = self.parse_statement(tokens)
            if statement is not None:
                extend_or_append(program.body, statement)
        return program
    
    def parse_block(self, tokens: list[Token]) -> Block:
        self.eat(tokens, TokenType.BLOCK_START)
        block = Block()
        while tokens[0].type != TokenType.BLOCK_END:
            statement = self.parse_statement(tokens)
            if statement is not None:
                extend_or_append(block.body, statement)
        self.eat(tokens, TokenType.BLOCK_END)
        return block

    def parse_statement(self, tokens: list[Token]) -> Statement | list[Statement] | None:
        if tokens[0].type == TokenType.STATEMENT_END:
            self.eat(tokens)
            return None
        if tokens[0].type == TokenType.BLOCK_START:
            return self.parse_block(tokens)
        if len(tokens) >= 2 and tokens[1].type == TokenType.ASSIGNMENT:
            return self.parse_assignment(tokens)
        
        if tokens[0].type == TokenType.KEYWORD:
            keyword = tokens[0].value
            if keyword in ['var', 'const']:
                return self.parse_assignment(tokens)
            if keyword == 'if':
                return self.parse_if_statement(tokens)
            if keyword in ['while', 'until']:
                return self.parse_repeat_statement(tokens)
            if keyword == 'function':
                return self.parse_function_declaration(tokens)
        statement = self.parse_join_expression(tokens)
        self.eat(tokens, TokenType.STATEMENT_END)
        return statement
    
    # Deprecated!
    # def parse_expression(self, tokens: list[Token]) -> Expression:
    #     if len(tokens) >= 2 and tokens[1].type == TokenType.COMPARE:
    #         if tokens[1].value in ['>=', '<=']:
    #             return self.parse_comparison_expression(tokens)
    #     return self.parse_join_expression(tokens)
    
    def parse_and_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['&&'], self.parse_or_expression)

    def parse_or_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['||'], self.parse_comparison_expression)

    def parse_comparison_expression(self, tokens) -> Expression | NoReturn:
        inverse = False
        if tokens[0].type == TokenType.OPERATOR and tokens[0].value == '!':
            self.eat(tokens)
            inverse = not inverse
        
        if tokens[0].type == TokenType.LEFT_PAREN:
            self.eat(tokens)  # eat TokenType.LEFT_PAREN
            comparison_expression = self.parse_and_expression(tokens)
            self.eat(tokens, TokenType.RIGHT_PAREN)
        elif tokens[0].type == TokenType.KEYWORD:
            if tokens[0].value in ['true', 'false']:
                boolean = self.eat(tokens).value == 'true'
                if inverse:
                    boolean = not boolean
                if boolean:
                    return FunctionCall('operator_not', [])  # not() -> true
                return FunctionCall('operator_not', [FunctionCall('operator_not', [])])  # not(true) -> false
            else:
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected keyword "true" or "false"'))
        else:
            left = self.parse_additive_expression(tokens)
            operator = self.eat(tokens, TokenType.COMPARE).value
            right = self.parse_additive_expression(tokens)
            if operator in ['in', 'contains']:
                if operator == 'in':
                    left, right = right, left  # Swap left and right
                comparison_expression = FunctionCall('operator_contains', [left, right])
            else:
                if operator in ['>=', '<=', '!=']:
                    operator = inverse_sign[operator]
                    inverse = not inverse
                comparison_expression = FunctionCall('operator_' + sign_to_english[operator], [left, right])
        
        if inverse:
            return FunctionCall('operator_' + sign_to_english['!'], [comparison_expression])
        return comparison_expression

    def _parse_expression(self, tokens: list[Token], operators: list[str], next_level: Callable) -> Expression:
        left = next_level(tokens)
        while tokens[0].type == TokenType.OPERATOR and tokens[0].value in operators:
            operator = self.eat(tokens).value
            right = next_level(tokens)
            left = FunctionCall('operator_' + sign_to_english[operator], [left, right])
        return left

    def parse_join_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['..'], self.parse_additive_expression)

    def parse_additive_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['+', '-'], self.parse_multiplicative_expression)

    def parse_multiplicative_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['*', '/', '%'], self.parse_subscript_expression)
    
    def parse_subscript_expression(self, tokens: list[Token]) -> Expression:
        left = self.parse_factor(tokens)
        if tokens[0].type == TokenType.SUBSCRIPT_LEFT:
            self.eat(tokens)  # eat TokenType.SUBSCRIPT_LEFT
            index = self.parse_join_expression(tokens)
            self.eat(tokens, TokenType.SUBSCRIPT_RIGHT)
            return FunctionCall('operator_letter_of', [left, index])
        return left

    def parse_factor(self, tokens: list[Token]) -> Expression:
        multiplier = 1
        while tokens[0].type == TokenType.OPERATOR and tokens[0].value in ['+', '-']:
            if self.eat(tokens).value == '-':
                multiplier *= -1
        factor = None

        if tokens[0].type == TokenType.INTEGER:
            value = self.eat(tokens).value  # eat TokenType.INTEGER
            base = 10
            if value.startswith('0') and value != '0':
                # 0o, 0b, 0x
                letter_to_base = {
                    'b': 2,
                    'o': 8,
                    'x': 16
                }
                base = letter_to_base[value[1]]
                value = value[2:]
            # Multiply on compiling
            factor = Number(int(value, base) * multiplier)
            multiplier = 1
        elif tokens[0].type == TokenType.FLOAT:
            value = self.eat(tokens).value  # eat TokenType.FLOAT
            if value.endswith('.'):
                value += '0'
            if value.startswith('.'):
                value = '0' + value
            factor = Number(float(value) * multiplier)
            multiplier = 1
        elif tokens[0].type == TokenType.LEFT_PAREN:
            self.eat(tokens)  # eat TokenType.LEFT_PAREN
            expression = self.parse_join_expression(tokens)
            self.eat(tokens, TokenType.RIGHT_PAREN)
            factor = expression
        elif tokens[0].type == TokenType.STRING:
            factor = String(self.eat(tokens).value)  # eat TokenType.STRING
        elif len(tokens) >= 2 and tokens[0].type == TokenType.IDENTIFIER and tokens[1].type == TokenType.LEFT_PAREN:
            factor = self.parse_function_call(tokens)
        elif tokens[0].type == TokenType.IDENTIFIER:
            factor = Identifier(self.eat(tokens).value)  # eat TokenType.STRING
        else:  # No any factor found
            raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected a factor'))
        
        if multiplier == 1:
            return factor
        return FunctionCall('operator_' + sign_to_english['*'], [factor, Number(multiplier)])

    def parse_function_call(self, tokens: list[Token]) -> FunctionCall:
        name = self.parse_identifier(tokens).name
        params = []
        self.eat(tokens, TokenType.LEFT_PAREN)
        if tokens[0].type != TokenType.RIGHT_PAREN:
            params.append(self.parse_join_expression(tokens))
            while tokens[0].type == TokenType.COMMA:
                self.eat(tokens)  # eat TokenType.COMMA   
                params.append(self.parse_join_expression(tokens))
        self.eat(tokens, TokenType.RIGHT_PAREN)
        return FunctionCall(name, params)

    def parse_identifier(self, tokens: list[Token]) -> Identifier:
        if tokens[0].type == TokenType.IDENTIFIER:
            return Identifier(self.eat(tokens).value)
        raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected an identifier (letters, "_", or numbers (not start))'))

    def parse_assignment(self, tokens: list[Token]) -> FunctionCall | VariableDeclaration | list[Statement] | NoReturn:
        is_declare = False
        if tokens[0].type == TokenType.KEYWORD:
            if tokens[0].value in ['const', 'var']:
                is_declare = True
                is_const = tokens[0].value == 'const'
                self.eat(tokens)  # eat TokenType.KEYWORD
            else:
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected "var", "const" or an identifier'))
        identifier = self.parse_identifier(tokens)
        if tokens[0].type != TokenType.ASSIGNMENT:  # No assignment
            if not is_declare:
                # Example: NOT_DECLARED = 1;
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected an assignment or a variable declaration'))
            if is_const:
                # Example: const SOME_CONST;
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected an assignment on a constant variable'))
            # Example: var SOME_VAR;
            return VariableDeclaration(identifier.name, False)
        if is_declare and tokens[0].value != '=':
            raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected "=" after variable declaration'))
        assignment_mode = self.eat(tokens).value  # eat TokenType.ASSIGNMENT
        expression = self.parse_join_expression(tokens)
        self.eat(tokens, TokenType.STATEMENT_END)
        if not is_declare:
            if assignment_mode == '=':
                return FunctionCall('data_setvariableto', [identifier, expression])
            elif assignment_mode == '+=':
                return FunctionCall('data_changevariableby', [identifier, expression])
            else:
                return FunctionCall('data_setvariableto', [identifier, FunctionCall('operator_' + sign_to_english[assignment_mode[0]], [identifier, expression])])
        if assignment_mode != '=':
            raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected "=" after variable declaration'))
        # Syntactic sugar: var SOME_VAR = 1;
        return [
            VariableDeclaration(identifier.name, is_const),  # var SOME_VAR;
            FunctionCall('data_setvariableto', [identifier, expression])  # SOME_VAR = 1;
        ]

    def parse_if_statement(self, tokens: list[Token]) -> FunctionCall:
        self.eat(tokens)  # eat TokenType.KEYWORD
        self.eat(tokens, TokenType.LEFT_PAREN)
        condition = self.parse_and_expression(tokens)
        self.eat(tokens, TokenType.RIGHT_PAREN)
        sub_stack = Block(self.parse_statement(tokens))
        if tokens[0].type == TokenType.KEYWORD:
            if tokens[0].value == 'else':
                self.eat(tokens)  # eat TokenType.KEYWORD
                sub_stack2 = Block(self.parse_statement(tokens))
                return FunctionCall('control_if_else', [condition, sub_stack, sub_stack2])
        return FunctionCall('control_if', [condition, sub_stack])

    def parse_repeat_statement(self, tokens: list[Token]) -> FunctionCall:
        mode = self.eat(tokens).value  # eat TokenType.KEYWORD, "while" or "until"
        self.eat(tokens, TokenType.LEFT_PAREN)
        condition = self.parse_and_expression(tokens)
        if mode == 'while':
            condition = FunctionCall('operator_' + sign_to_english['!'], [condition])
        self.eat(tokens, TokenType.RIGHT_PAREN)
        sub_stack = Block(self.parse_statement(tokens))
        return FunctionCall('control_repeat_until', [condition, sub_stack])

    def parse_function_declaration(self, tokens: list[Token]) -> FunctionDeclaration:
        self.eat(tokens)  # eat TokenType.KEYWORD
        name = self.parse_identifier(tokens).name
        self.eat(tokens, TokenType.LEFT_PAREN)
        params = []
        if tokens[0].type != TokenType.RIGHT_PAREN:
            params.append(self.parse_identifier(tokens).name)
            while tokens[0].type == TokenType.COMMA:
                self.eat(tokens)  # eat TokenType.COMMA
                params.append(self.parse_identifier(tokens).name)
        self.eat(tokens, TokenType.RIGHT_PAREN)
        sub_stack = Block(self.parse_statement(tokens))
        return FunctionDeclaration(name, params, sub_stack)
