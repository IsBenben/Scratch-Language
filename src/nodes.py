# *-* encoding: utf-8 *-*
"""
Copyright (c) Copyright 2024 Scratch-Language Developers
https://github.com/IsBenben/Scratch-Language
License under the Apache License, version 2.0
"""

from __future__ import annotations
from utils import generate_id
import copy
from typing import TypeVar

INDENT = '  '

class Node:
    def node_type_name(self) -> str:
        return type(self).__name__
    
    def dump(self, indent=''):
        return ''

    @staticmethod
    def dump_list(list, indent='') -> str:
        if not list:
            return indent + '[*No elements*]\n'
        result = indent + '[\n'
        for item in list:
            if isinstance(item, Node):
                result += item.dump(indent + INDENT)
            else:
                result += indent + INDENT + item + '\n'
        result += indent + ']\n'
        return result
    
    # Support for "copy" module
    @property
    def _copy_keys(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __copy__(self):
        return type(self)(**self._copy_keys)

    def __deepcopy__(self, memo):
        return type(self)(**copy.deepcopy(self._copy_keys, memo))

class Statement(Node):
    def dump(self, indent=''):
        return indent + 'Statement {N/A}\n'

STATEMENT_TYPE = None | list[Statement] | Statement

class Block(Statement):
    def __init__(self, body: STATEMENT_TYPE = None):
        if isinstance(body, Block):
            body = body.body
        if body is None:
            body = []
        if isinstance(body, Statement):
            body = [body]
        self.body: list[Statement] = body
    
    def dump(self, indent=''):
        result = indent + 'Block {\n'
        result += Node.dump_list(self.body, indent + INDENT)
        result += indent + '}\n'
        return result

class Program(Block):
    def dump(self, indent=''):
        result = indent + 'Program {\n'
        result += Node.dump_list(self.body, indent + INDENT)
        result += indent + '}\n'
        return result

class Expression(Statement):
    def dump(self, indent=''):
        return indent + 'Expression {N/A}\n'

class Factor(Expression):
    def dump(self, indent=''):
        return indent + 'Factor {N/A}\n'

class Number(Factor):
    def __init__(self, value: float):
        self.value: float = value
    
    def dump(self, indent=''): 
        return indent + 'Number ' + str(self.value) + '\n'

class String(Factor):
    def __init__(self, value: str):
        self.value: str = value
    
    def dump(self, indent=''): 
        return indent + 'String ' + str(self.value) + '\n'

# Boolean implement with FunctionCall

def create_boolean(boolean: bool | Node) -> FunctionCall:
    if boolean is True:
        return FunctionCall('operator_not', [])  # not() -> true
    if boolean is False:
        return FunctionCall('operator_not', [FunctionCall('operator_not', [])])  # not(true) -> false
    assert isinstance(boolean, Node)
    if not is_boolean(boolean):
        raise ValueError('Node is not a boolean')
    return create_boolean(value_of_boolean(boolean))

def is_boolean(node: Node) -> bool:
    if not isinstance(node, FunctionCall) or not node.always_builtin:
        return False
    is_boolean_arg = len(node.args) == 0 \
                         or len(node.args) == 1 \
                         and is_boolean(node.args[0])
    return node.name == 'operator_not' \
               and is_boolean_arg

def value_of_boolean(node: Node) -> bool:
    if not is_boolean(node):
        raise ValueError('Node is not a boolean')
    assert isinstance(node, FunctionCall)
    if len(node.args) == 0:  # not() -> true
        return True
    return not value_of_boolean(node.args[0])

class Identifier(Factor):
    def __init__(self, name: str):
        self.name: str = name
    
    def dump(self, indent=''):
        return indent + 'Identifier ' + self.name + '\n'

class FunctionCall(Factor):
    def __init__(self, name: str, args: list[Statement], always_builtin: bool = True):
        self.name: str = name
        self.args: list[Statement] = args
        self.always_builtin: bool = always_builtin
    
    def dump(self, indent=''):
        result = indent + 'FunctionCall {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += Node.dump_list(self.args, indent + INDENT)
        result += indent + INDENT + '[bool] ' + str(self.always_builtin) + '\n'
        result += indent + '}\n'
        return result

class VariableDeclaration(Statement):
    def __init__(self, name: str, is_const: bool, is_array: bool):
        self.name: str = name
        if is_const and is_array:
            raise ValueError('Variable cannot be both constant and an array')
        self.is_const: bool = is_const
        self.is_array: bool = is_array
    
    def dump(self, indent=''):
        result = indent + 'VariableDeclaration {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += indent + INDENT + '[bool] ' + str(self.is_const) + '\n'
        result += indent + INDENT + '[bool] ' + str(self.is_array) + '\n'
        result += indent + '}\n'
        return result

class FunctionDeclaration(Statement):
    def __init__(self, name: str, args: list[str], body: Block, attributes: list[str]):
        self.name: str = name
        self.args: list[str] = args
        self.body: Block = body
        self.attributes: list[str] = attributes
    
    def dump(self, indent=''):
        result = indent + 'FunctionDeclaration {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += self.dump_list(self.args, indent + INDENT)
        result += self.body.dump(indent + INDENT)
        result += self.dump_list(self.attributes, indent + INDENT)
        result += indent + '}\n'
        return result

class Custom(Block):
    def __init__(self, name: str):
        self.name: str = name
    
    def dump(self, indent=''):
        return indent + 'Custom ' + self.name + '\n'

class Clone(Statement):
    def __init__(self, clone: Block):
        self.clone = clone
        self._clone_comparison = FunctionCall('control_if', [
            FunctionCall('operator_equals', [
                Identifier(generate_id(('variable', 'clone', None))),
                String(generate_id(('clone', self))),
            ]),
            clone,
        ])
        self._parent = Block([
            FunctionCall('data_setvariableto', [
                Identifier(generate_id(('variable', 'clone', None))),
                String(generate_id(('clone', self)))
            ]),
            FunctionCall('control_create_clone_of', [
                FunctionCall('control_create_clone_of_menu', [Custom('_myself_')])
            ],
        )])
    
    def dump(self, indent=''):
        result = indent + 'Clone {\n'
        result += self.clone.dump(indent + INDENT)
        result += indent + '}\n'
        return result

class ListIdentifier(Identifier):
    def __init__(self, name: str | Identifier):
        self.name: str = name if isinstance(name, str) else name.name

class Macro(Statement):
    def __init__(self, name: str, args: list[str], body: STATEMENT_TYPE):
        self.name: str = name
        self.args: list[str] = args
        self.body: None | list[Statement] | Statement = body

class NodeVisitor:
    def visit(self, node: Node):
        return getattr(self, 'visit_' + type(node).__name__, self.visit_error)(node)
    
    def visit_Statement(self, node: Statement):
        pass

    def visit_Block(self, node: Block):
        for statement in node.body:
            self.visit(statement)

    def visit_Program(self, node: Program):
        for statement in node.body:
            self.visit(statement)

    def visit_Expression(self, node: Expression):
        pass
    
    def visit_Factor(self, node: Factor):
        pass

    def visit_Number(self, node: Number):
        pass
    
    def visit_String(self, node: String):
        pass

    def visit_Identifier(self, node: Identifier):
        pass
    
    def visit_FunctionCall(self, node: FunctionCall):
        for arg in node.args:
            self.visit(arg)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        pass

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        self.visit(node.body)

    def visit_Custom(self, node: Custom):
        pass

    def visit_Clone(self, node: Clone):
        pass

    def visit_ListIdentifier(self, node: ListIdentifier):
        pass

    def visit_error(self, node: Node):
        raise TypeError(f'Method visit_{type(node).__name__} is not defined')

class NodeTransformer(NodeVisitor):
    # visit_xxx method usage:
    # return Node: replace with
    # return None: keep old

    def visit_Block(self, node: Block):
        for i, statement in enumerate(node.body):
            result = self.visit(statement)
            if result is not None:
                node.body[i] = result
        return node

    def visit_Program(self, node: Program):
        for i, statement in enumerate(node.body):
            result = self.visit(statement)
            if result is not None:
                node.body[i] = result
        return node
    
    def visit_FunctionCall(self, node: FunctionCall):
        for i, arg in enumerate(node.args):
            result = self.visit(arg)
            if result is not None:
                node.args[i] = result
        return node

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        result = self.visit(node.body)
        if result is not None:
            node.body = result
        return node
    
    def visit_Clone(self, node: Clone):
        result = self.visit(node.clone)
        if result is not None:
            node.clone = result
        return node

    def visit_error(self, node: Node):
        raise TypeError(f'Method visit_{type(node).__name__} is not defined')
