from __future__ import annotations
from utils import generate_id
import copy
from typing import TypeVar

INDENT = ' |  '

class Node:
    def node_type_name(self) -> str:
        return type(self).__name__
    
    def dump(self, indent=''):
        return ''

    @staticmethod
    def dump_list(list, indent='') -> str:
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
    def __init__(self, body: STATEMENT_TYPE | Block = None):
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

class Identifier(Factor):
    def __init__(self, name: str):
        self.name: str = name
    
    def dump(self, indent=''):
        return indent + 'Identifier ' + self.name + '\n'

class FunctionCall(Factor):
    def __init__(self, name: str, args: list[Statement]):
        self.name: str = name
        self.args: list[Statement] = args
    
    def dump(self, indent=''):
        result = indent + 'FunctionCall {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += Node.dump_list(self.args, indent + INDENT)
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
    def __init__(self, name: str, args: list[str], body: Block):
        self.name: str = name
        self.args: list[str] = args
        self.body: Block = body
    
    def dump(self, indent=''):
        result = indent + 'FunctionDeclaration {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += self.dump_list(self.args, indent + INDENT)
        result += self.body.dump(indent + INDENT)
        result += indent + '}\n'
        return result

class Custom(Block):
    def __init__(self, name: str):
        self.name: str = name
    
    def dump(self, indent=''):
        return indent + 'Custom ' + self.name + '\n'

class Clone(Statement):
    def __init__(self, clone: Block):
        self.clone = FunctionCall('control_if', [
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
        pass

    def visit_Program(self, node: Program):
        pass

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
        pass

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        pass

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        pass

    def visit_Custom(self, node: Custom):
        pass

    def visit_Clone(self, node: Clone):
        pass

    def visit_ListIdentifier(self, node: ListIdentifier):
        pass

    def visit_error(self, node: Node):
        raise TypeError(f'Method visit_{type(node).__name__} is not defined')
