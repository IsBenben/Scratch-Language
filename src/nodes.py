from __future__ import annotations

INDENT = ' |  '

class Node:
    def node_type_name(self) -> str:
        return type(self).__name__
    
    @staticmethod
    def dump_list(list, indent='') -> str:
        result = indent + '[\n'
        for item in list:
            result += item.dump(indent + INDENT)
        result += indent + ']\n'
        return result

class Statement(Node):
    def dump(self, indent=''):
        return indent + 'Statement {N/A}\n'

class Block(Statement):
    def __init__(self, body: None | list[Statement] | Statement | Block = None):
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
    def __init__(self, value: int):
        self.value: int = value
    
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
    def __init__(self, name: str, is_const: bool):
        self.name: str = name
        self.is_const: bool = is_const
    
    def dump(self, indent=''):
        result = indent + 'VariableDeclaration {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += indent + INDENT + '[bool] ' + str(self.is_const) + '\n'
        result += indent + '}\n'

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

    def visit_error(self, node: Node):
        raise TypeError(f'Method visit_{type(node).__name__} is not defined')
