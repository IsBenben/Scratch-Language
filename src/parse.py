from __future__ import annotations
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

class Record:
    def __init__(self, block: list[Statement], parent: Record | None = None):
        self.block = block
        self.variables: dict[str, VariableDeclaration] = {}
        self.parent: Record | None = parent
    
    def variable_declaration(self, name: str, *args, **kwargs):
        result = VariableDeclaration(name, *args, **kwargs)
        self.variables[name] = result
        return result

    def resolve(self, name: str) -> VariableDeclaration | None:
        # Check error in interpret, not in parse
        if name in self.variables:
            return self.variables[name]
        if self.parent is not None:
            return self.parent.resolve(name)
        return None

class Parser:
    def parse(self, code: str) -> Program:
        self.record: Record | None = None
        return self.parse_program(tokenize(code))
    
    def eat(self, tokens: list[Token], type: Optional[TokenType]=None) -> Token:
        if type is None:
            return tokens.pop(0)
        if tokens[0].type == type:
            return tokens.pop(0)
        raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected {type}'))

    def parse_program(self, tokens: list[Token]) -> Program:
        program = Program()
        old_record = self.record
        self.record = Record(program.body, old_record)
        while tokens[0].type != TokenType.EOF:
            statement = self.parse_statement(tokens)
            if statement is not None:
                extend_or_append(program.body, statement)
        self.record = old_record
        return program
    
    def parse_block(self, tokens: list[Token]) -> Block:
        self.eat(tokens, TokenType.BLOCK_START)
        block = Block()
        old_record = self.record
        self.record = Record(block.body, old_record)
        while tokens[0].type != TokenType.BLOCK_END:
            statement = self.parse_statement(tokens)
            if statement is not None:
                extend_or_append(block.body, statement)
        self.eat(tokens, TokenType.BLOCK_END)
        self.record = old_record
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
            if keyword in ['var', 'const', 'array']:
                return self.parse_assignment(tokens)
            if keyword == 'if':
                return self.parse_if_statement(tokens)
            if keyword in ['while', 'until']:
                return self.parse_repeat_statement(tokens)
            if keyword == 'function':
                return self.parse_function_declaration(tokens)
            if keyword == 'clone':
                return self.parse_clone_statement(tokens)
            if keyword == 'delete':
                return self.parse_delete(tokens)
            if keyword == 'for':
                return self.parse_for_statement(tokens)
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

    def parse_comparison_expression(self, tokens: list[Token]) -> Expression | NoReturn:
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
            left = self.parse_join_expression(tokens)
            if isinstance(left, ListIdentifier):
                raise_error(Error('Parse', f'Cannot compare list "{left.name}" with another expression'))
            operator = self.eat(tokens, TokenType.COMPARE).value
            right = self.parse_join_expression(tokens)
            if isinstance(right, ListIdentifier):
                raise_error(Error('Parse', f'Cannot compare list "{right.name}" with another expression'))
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

    def _parse_expression(self, tokens: list[Token], operators: list[str], next_level: Callable[[list[Token]], Expression]) -> Expression:
        left = next_level(tokens)
        while tokens[0].type == TokenType.OPERATOR and tokens[0].value in operators:
            operator = self.eat(tokens).value
            right = next_level(tokens)
            is_array = isinstance(right, ListIdentifier)
            if is_array != isinstance(left, ListIdentifier):
                raise_error(Error('Parse', f'Cannot use operator "{operator}" with different types'))
            if is_array:
                if operator == '+' or operator == '..':
                    assert self.record is not None

                    result = ListIdentifier('')
                    result.name = generate_id(('array', 'join', result))
                    index = Identifier(generate_id(('array', 'index', result)))
                    # # Pseudo Code:
                    # result = []
                    # index = 0
                    # while index < len(left):
                    #     index += 1
                    #     result.append(left[i]) # 1-based index in Scratch
                    # index = 0
                    # while index < len(right):
                    #     index += 1
                    #     result.append(right[i])
                    self.record.block.extend([
                        self.record.variable_declaration(result.name, False, True),
                        self.record.variable_declaration(index.name, False, False),
                        FunctionCall('data_setvariableto', [index, Number(0)]),
                        FunctionCall('control_repeat', [
                            FunctionCall('data_lengthoflist', [left]),
                            Block([
                                FunctionCall('data_changevariableby', [index, Number(1)]),
                                FunctionCall('data_addtolist', [result, FunctionCall('data_itemoflist', [left, index])])
                            ])
                        ]),
                        FunctionCall('data_setvariableto', [index, Number(0)]),
                        FunctionCall('control_repeat', [
                            FunctionCall('data_lengthoflist', [right]),
                            Block([
                                FunctionCall('data_changevariableby', [index, Number(1)]),
                                FunctionCall('data_addtolist', [result, FunctionCall('data_itemoflist', [right, index])])
                            ])
                        ]),
                    ])
                    left = result
                else:
                    raise_error(Error('Parse', f'Cannot use operator "{operator}" with two arrays'))
            else:
                left = FunctionCall('operator_' + sign_to_english[operator], [left, right])
        return left

    def parse_join_expression(self, tokens: list[Token]) -> Expression:
        assert self.record is not None

        left = self._parse_expression(tokens, ['..'], self.parse_additive_expression)
        if tokens[0].type == TokenType.OPERATOR and tokens[0].value == '->':
            if isinstance(left, ListIdentifier):
                raise_error(Error('Parse', 'Cannot use "->" operator with array'))
            self.eat(tokens)  # eat TokenType.OPERATOR
            right = self.parse_join_expression(tokens)
            if isinstance(right, ListIdentifier):
                raise_error(Error('Parse', 'Cannot use "->" operator with array'))
            
            # # Pseudo Code:
            # result = []
            # i = left
            # while i <= right:
            #    result.append(i)
            #    i += 1
            result = ListIdentifier('')
            result.name = generate_id(('array', 'range', result))
            index = Identifier(generate_id(('array', 'index', result)))
            self.record.block.extend([
                self.record.variable_declaration(result.name, False, True),
                self.record.variable_declaration(index.name, False, False),
                FunctionCall('data_deletealloflist', [result]),
                FunctionCall('data_setvariableto', [index, left]),
                FunctionCall('control_repeat_until', [
                    FunctionCall('operator_gt', [index, right]),
                    Block([
                        FunctionCall('data_addtolist', [result, index]),
                        FunctionCall('data_changevariableby', [index, Number(1)]),
                    ])
                ]),
            ])
            left = result
        return left

    def parse_additive_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['+', '-'], self.parse_multiplicative_expression)

    def parse_multiplicative_expression(self, tokens: list[Token]) -> Expression:
        return self._parse_expression(tokens, ['*', '/', '%'], self.parse_subscript_expression)
    
    def parse_subscript_expression(self, tokens: list[Token]) -> Expression | NoReturn:
        left = self.parse_factor(tokens)
        item_of_list = None
        if tokens[0].type == TokenType.SUBSCRIPT_LEFT:
            self.eat(tokens)  # eat TokenType.SUBSCRIPT_LEFT
            index = self.parse_join_expression(tokens)
            self.eat(tokens, TokenType.SUBSCRIPT_RIGHT)
            if isinstance(left, ListIdentifier):
                item_of_list = [left, index]
                left = FunctionCall('data_itemoflist', item_of_list)
            else:
                left = FunctionCall('operator_letter_of', [left, index])
        if tokens[0].type == TokenType.ASSIGNMENT:
            if not item_of_list:
                raise_error(Error('Parse', 'Cannot set item of non-array'))
            if self.eat(tokens).value != '=':
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected "=" after array set item'))
            expression = self.parse_join_expression(tokens)
            left = FunctionCall('data_replaceitemoflist', item_of_list + [expression])
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
        elif tokens[0].type == TokenType.SUBSCRIPT_LEFT:
            return self.parse_array(tokens)
        elif tokens[0].type == TokenType.STRING:
            factor = String(self.eat(tokens).value)  # eat TokenType.STRING
        elif len(tokens) >= 2 and tokens[0].type == TokenType.IDENTIFIER and tokens[1].type == TokenType.LEFT_PAREN:
            factor = self.parse_function_call(tokens)
        elif tokens[0].type == TokenType.IDENTIFIER:
            factor = self.parse_identifier(tokens)
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
        assert self.record is not None

        if tokens[0].type == TokenType.IDENTIFIER:
            name = self.eat(tokens).value
            variable = self.record.resolve(name)
            if variable and variable.is_array:
                return ListIdentifier(name)
            return Identifier(name)
        raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected an identifier (letters, "_", or numbers (not start))'))

    def parse_array(self, tokens: list[Token]) -> ListIdentifier:
        assert self.record is not None

        name = ListIdentifier('')
        name.name = generate_id(('array', 'literal', name))
        self.eat(tokens, TokenType.SUBSCRIPT_LEFT)
        self.record.block.append(self.record.variable_declaration(name.name, False, True))
        self.record.block.append(FunctionCall('data_deletealloflist', [name]))
        if tokens[0].type != TokenType.SUBSCRIPT_RIGHT:
            self.record.block.append(FunctionCall('data_addtolist', [name, self.parse_join_expression(tokens)]))
            while tokens[0].type == TokenType.COMMA:
                self.eat(tokens)  # eat TokenType.COMMA
                self.record.block.append(FunctionCall('data_addtolist', [name, self.parse_join_expression(tokens)]))
        self.eat(tokens, TokenType.SUBSCRIPT_RIGHT)
        return name

    def parse_assignment(self, tokens: list[Token]) -> FunctionCall | VariableDeclaration | list[Statement] | Block | NoReturn:
        assert self.record is not None
        
        is_declare = False
        if tokens[0].type == TokenType.KEYWORD:
            if tokens[0].value in ['const', 'var', 'array']:
                is_declare = True
                is_const = tokens[0].value == 'const'
                is_array = tokens[0].value == 'array'
                self.eat(tokens)  # eat TokenType.KEYWORD
            else:
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected "var", "const", "array" or an identifier'))
        identifier = self.parse_identifier(tokens)
        if tokens[0].type != TokenType.ASSIGNMENT:  # No assignment
            if not is_declare:
                # Example: NOT_DECLARED = 1;
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected an assignment or a variable declaration'))
            if is_const:
                # Example: const SOME_CONST;
                raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected an assignment on a constant variable'))
            # Example: var SOME_VAR;
            return self.record.variable_declaration(identifier.name, False, is_array)
        if is_declare and tokens[0].value != '=':
            raise_error(Error('Parse', f'Unexpected token "{tokens[0].desc}", expected "=" after variable declaration'))
        assignment_node = self.eat(tokens)  # eat TokenType.ASSIGNMENT
        expression = self.parse_join_expression(tokens)
        self.eat(tokens, TokenType.STATEMENT_END)
        
        if assignment_node.value == '=':
            if isinstance(expression, ListIdentifier):
                index = Identifier(generate_id(('array', 'index', identifier)))
                # # Pseudo Code:
                # index = 0
                # identifier.clear()
                # while index < len(expression):
                #     identifier.append(expression[index])
                assignment = Block([
                    self.record.variable_declaration(index.name, False, False),
                    FunctionCall('data_deletealloflist', [identifier]),
                    FunctionCall('data_setvariableto', [index, Number(0)]),
                    FunctionCall('control_repeat', [
                        FunctionCall('data_lengthoflist', [expression]),
                        Block([
                            FunctionCall('data_changevariableby', [index, Number(1)]),
                            FunctionCall('data_addtolist', [identifier, FunctionCall('data_itemoflist', [expression, index])])
                        ])
                    ]),
                ])
            else:
                assignment = FunctionCall('data_setvariableto', [identifier, expression])
        elif assignment_node.value == '+=':
            if isinstance(expression, ListIdentifier):
                index = Identifier(generate_id(('array', 'index', identifier)))
                assignment = Block([
                    self.record.variable_declaration(index.name, False, False),
                    # Only no "FunctionCall('data_deletealloflist', [identifier]),"
                    FunctionCall('data_setvariableto', [index, Number(0)]),
                    FunctionCall('control_repeat', [
                        FunctionCall('data_lengthoflist', [expression]),
                        Block([
                            FunctionCall('data_changevariableby', [index, Number(1)]),
                            FunctionCall('data_addtolist', [identifier, FunctionCall('data_itemoflist', [expression, index])])
                        ])
                    ]),
                ])
            else:
                assignment = FunctionCall('data_changevariableby', [identifier, expression])
        else:
            if isinstance(expression, ListIdentifier):
                raise_error(Error('Parse', f'Unexpected token "{assignment_node.desc}", expected "=" or "+=" after list assignment'))
            else:
                assignment = FunctionCall('data_setvariableto', [identifier, FunctionCall('operator_' + sign_to_english[assignment_node.value[0]], [identifier, expression])])

        if not is_declare:
            return assignment
        if assignment_node.value != '=':
            raise_error(Error('Parse', f'Unexpected token "{assignment_node.desc}", expected "=" after variable declaration assignment'))
        # Syntactic sugar: var SOME_VAR = 1;
        return [
            self.record.variable_declaration(identifier.name, is_const, is_array),  # var SOME_VAR;
            assignment  # SOME_VAR = 1;
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
        assert self.record is not None

        self.eat(tokens)  # eat TokenType.KEYWORD
        name = self.parse_identifier(tokens).name
        self.eat(tokens, TokenType.LEFT_PAREN)
        params = []
        if tokens[0].type != TokenType.RIGHT_PAREN:
            params.append(self.parse_identifier(tokens).name)
            self.record.variable_declaration(params[-1], False, False)
            while tokens[0].type == TokenType.COMMA:
                self.eat(tokens)  # eat TokenType.COMMA
                params.append(self.parse_identifier(tokens).name)
                self.record.variable_declaration(params[-1], False, False)
        self.eat(tokens, TokenType.RIGHT_PAREN)
        sub_stack = Block(self.parse_statement(tokens))
        return FunctionDeclaration(name, params, sub_stack)

    def parse_clone_statement(self, tokens: list[Token]) -> Clone:
        self.eat(tokens)  # eat TokenType.KEYWORD
        clone = Block(self.parse_statement(tokens))
        return Clone(clone)

    def parse_delete(self, tokens: list[Token]) -> FunctionCall:
        self.eat(tokens)  # eat TokenType.KEYWORD
        name = self.parse_identifier(tokens)
        if not isinstance(name, ListIdentifier):
            raise_error(Error('Parse', f'Expected a list identifier, got "{name}"'))
        self.eat(tokens, TokenType.SUBSCRIPT_LEFT)
        index = self.parse_join_expression(tokens)
        self.eat(tokens, TokenType.SUBSCRIPT_RIGHT)
        return FunctionCall('data_deleteoflist', [name, index])

    def parse_for_statement(self, tokens: list[Token]) -> Block:
        assert self.record is not None

        self.eat(tokens)  # eat TokenType.KEYWORD
        self.eat(tokens, TokenType.LEFT_PAREN)
        var = self.parse_identifier(tokens)
        index = Identifier(generate_id(('for_each', var)))
        assignment = self.eat(tokens, TokenType.ASSIGNMENT)
        if assignment.value != '=':
            raise_error(Error('Parse', f'Unexpected token "{assignment.desc}", expected "="'))
        sequence = self.parse_join_expression(tokens)
        if not isinstance(sequence, ListIdentifier):
            raise_error(Error('Parse', f'Expected a list identifier'))
        self.eat(tokens, TokenType.RIGHT_PAREN)
        body = Block(self.parse_statement(tokens))
        return Block([
            self.record.variable_declaration(var.name, False, False),
            self.record.variable_declaration(index.name, False, False),
            FunctionCall('data_setvariableto', [index, Number(0)]),
            FunctionCall('control_repeat_until', [
                FunctionCall('operator_equals', [
                    index,
                    FunctionCall('data_lengthoflist', [sequence])
                ]),
                Block([
                    FunctionCall('data_changevariableby', [index, Number(1)]),
                    FunctionCall('data_setvariableto', [
                        var,
                        FunctionCall('data_itemoflist', [sequence, index])
                    ]),
                ] + body.body)
            ])
        ])
