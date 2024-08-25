from tokens import TokenType, tokenize, Token
from nodes import *
from error import Error, raise_error
from typing import Optional

class Parser:
    def parse(self, code: str):
        return self.parse_program(tokenize(code))
    
    def eat(self, tokens: list[Token], type: Optional[TokenType]=None) -> Token:
        if type is None:
            return tokens.pop(0)
        if tokens[0].type == type:
            return tokens.pop(0)
        raise_error(Error('Parse', 'Unexpected token "{}", expected {}'.format(tokens[0].value, type)))

    def parse_program(self, tokens: list[Token]) -> Program:
        program = Program()
        while tokens[0].type != TokenType.EOF:
            statement = self.parse_statement(tokens)
            if statement is not None:
                program.body.append(statement)
        return program
    
    def parse_block(self, tokens: list[Token]) -> Block:
        self.eat(tokens, TokenType.BLOCK_START)
        block = Block()
        while tokens[0].type != TokenType.BLOCK_END:
            statement = self.parse_statement(tokens)
            if statement is not None:
                block.body.append(statement)
        self.eat(tokens, TokenType.BLOCK_END)
        return block

    def parse_statement(self, tokens: list[Token]) -> Statement | None:
        if tokens[0].type == TokenType.SEMICOLON:
            self.eat(tokens)
            return None
        if tokens[0].type == TokenType.BLOCK_START:
            return self.parse_block(tokens)
        statement = self.parse_expression(tokens)
        self.eat(tokens, TokenType.SEMICOLON)
        return statement
    
    def parse_expression(self, tokens: list[Token]) -> Expression:
        return self.parse_additive_expression(tokens)
    
    def parse_additive_expression(self, tokens: list[Token]) -> Expression:
        left = self.parse_multiplicative_expression(tokens)
        while tokens[0].type == TokenType.BINARY_OPERATOR and tokens[0].value in ['+', '-']:
            operator = self.eat(tokens).value
            right = self.parse_multiplicative_expression(tokens)
            left = BinaryExpression(left, operator, right)
        return left

    def parse_multiplicative_expression(self, tokens: list[Token]) -> Expression:
        left = self.parse_factor(tokens)
        while tokens[0].type == TokenType.BINARY_OPERATOR and tokens[0].value in ['*', '/', '%']:
            operator = self.eat(tokens).value
            right = self.parse_factor(tokens)
            left = BinaryExpression(left, operator, right)
        return left
    
    def parse_factor(self, tokens: list[Token]) -> Expression:
        if tokens[0].type == TokenType.NUMBER:
            value = self.eat(tokens).value  # eat TokenType.NUMBER
            return Number(int(value))
        if tokens[0].type == TokenType.LEFT_PAREN:
            self.eat(tokens)  # eat TokenType.LEFT_PAREN
            expression = self.parse_expression(tokens)
            self.eat(tokens, TokenType.RIGHT_PAREN)
            return expression
        if tokens[0].type == TokenType.STRING:
            return String(self.eat(tokens).value)  # eat TokenType.STRING
        if tokens[0].type == TokenType.NULL:
            self.eat(tokens)  # eat TokenType.NULL
            return Null()
        if len(tokens) >= 2 and tokens[0].type == TokenType.IDENTIFIER and tokens[1].type == TokenType.LEFT_PAREN:
            return self.parse_function_call(tokens)
        
        raise_error(Error('Parse', 'Unexpected token "{}", expected a factor.'.format(tokens[0].value)))

    def parse_function_call(self, tokens: list[Token]) -> FunctionCall:
        name = self.parse_identifier(tokens).name
        params = []
        self.eat(tokens, TokenType.LEFT_PAREN)
        if tokens[0].type != TokenType.RIGHT_PAREN:
            params.append(self.parse_expression(tokens))
            while tokens[0].type == TokenType.COMMA:
                self.eat(tokens)  # eat TokenType.COMMA   
                params.append(self.parse_expression(tokens))
        self.eat(tokens, TokenType.RIGHT_PAREN)
        return FunctionCall(name, params)

    def parse_identifier(self, tokens: list[Token]) -> Identifier:
        if tokens[0].type == TokenType.IDENTIFIER:
            return Identifier(self.eat(tokens).value)
        raise_error(Error('Parse', 'Unexpected token "{}", expected an identifier (letters, "_", or numbers (not start)).'.format(tokens[0].value)))

    def parse_assignment(self, tokens: list[Token]) -> Assignment:
        identifier = self.parse_identifier(tokens)
        self.eat(tokens, TokenType.ASSIGNMENT)
        expression = self.parse_expression(tokens)
        return Assignment(identifier.name, expression)
