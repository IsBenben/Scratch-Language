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
    def __init__(self):
        self.body: list[Statement] = []
    
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

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left: Expression = left
        self.operator: str = operator
        self.right: Expression = right
    
    def dump(self, indent=''):
        result = indent + 'BinaryExpressionExpression {\n'
        result += self.left.dump(indent + INDENT)
        result += indent + INDENT + '[str] ' + self.operator + '\n'
        result += self.right.dump(indent + INDENT)
        result += indent + '}\n'
        return result

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
    def __init__(self, name: str, args: list[Expression]):
        self.name: str = name
        self.args: list[Expression] = args
    
    def dump(self, indent=''):
        result = indent + 'FunctionCall {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += Node.dump_list(self.args, indent + INDENT)
        result += indent + '}\n'
        return result
        
class Assignment(Statement):
    def __init__(self, name: str, value: Expression):
        self.name: str = name
        self.value: Expression = value
    
    def dump(self, indent=''):
        result = indent + 'Assignment {\n'
        result += indent + INDENT + '[str] ' + self.name + '\n'
        result += self.value.dump(indent + INDENT)
        result += indent + '}\n'

class NodeVisitor:
    def visit(self, node):
        return getattr(self, 'visit_' + type(node).__name__, self.visit_error)(node)
    
    def visit_Statement(self, node: Statement):
        pass

    def visit_Block(self, node: Block):
        for statement in node.body:
            self.visit(statement)

    def visit_Program(self, node: Program):
        self.visit_Block(node)

    def visit_Expression(self, node: Expression):
        pass
    
    def visit_BinaryExpression(self, node: BinaryExpression):
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_Factor(self, node: Factor):
        pass

    def visit_Number(self, node: Number):
        return node.value
    
    def visit_String(self, node: String):
        return node.value

    def visit_Identifier(self, node: Identifier):
        return node.name
    
    def visit_FunctionCall(self, node: FunctionCall):
        for arg in node.args:
            self.visit(arg)

    def visit_Assignment(self, node: Assignment):
        self.visit(node.value)

    def visit_error(self, node: Node):
        raise TypeError(f'Method visit_{type(node).__name__} is not defined.')
