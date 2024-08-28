from error import Error, raise_error
from records import Record
from nodes import Block, NodeVisitor, String
import json
from values import *
from utils import generate_id

BLOCK_TYPES: dict[str, dict[str, tuple]] = {
    'looks_say': {'inputs': ('MESSAGE',)},
    'looks_sayforsecs': {'inputs': ('MESSAGE', 'SECS')},
    'operator_add': {'inputs': ('NUM1', 'NUM2')},
    'operator_subtract': {'inputs': ('NUM1', 'NUM2')},
    'operator_multiply': {'inputs': ('NUM1', 'NUM2')},
    'operator_divide': {'inputs': ('NUM1', 'NUM2')},
    'operator_mod': {'inputs': ('NUM1', 'NUM2')},
    'operator_mod': {'inputs': ('NUM1', 'NUM2')},
    'data_setvariableto': {'inputs': ('VALUE',), 'fields': ('VARIABLE',)},
    'operator_and': {'inputs': ('OPERAND1', 'OPERAND2')},
    'operator_or': {'inputs': ('OPERAND1', 'OPERAND2')},
    'operator_not': {'inputs': ('OPERAND',)},
    'control_if': {'inputs': ('CONDITION', 'SUBSTACK')},
    'operator_gt': {'inputs': ('OPERAND1', 'OPERAND2')},
    'operator_lt': {'inputs': ('OPERAND1', 'OPERAND2')},
    'operator_equals': {'inputs': ('OPERAND1', 'OPERAND2')},
}
for value in BLOCK_TYPES.values():
    value.setdefault('fields', ())
    value.setdefault('inputs', ())

class Interpreter(NodeVisitor):
    def __init__(self) -> None:
        self.record = Record()
        self.project: dict = json.load(open('./src/model.json', encoding='utf-8'))
        self.blocks: dict[str, dict] = self.project['targets'][1]['blocks']
        self.variables: dict[str, list[str]] = self.project['targets'][0]['variables']
    
    def visit_Block(self, node) -> BlockList | None:
        if not node.body:
            return None
        start_id = end_id = None
        event = None

        # Run in new record
        old_record = self.record
        self.record = Record(self.record)

        for statement in node.body:
            block = self.visit(statement)
            if isinstance(block, BlockList):
                # Simple understand: doubly linked lists
                statement_start, statement_end = block.get_start_end()
                if start_id is None:
                    start_id = statement_start
                if event is not None:
                    self.blocks[statement_start]['parent'] = end_id
                    event['next'] = statement_start
                end_id = statement_end
                event = self.blocks[end_id]
            elif block is not None:
                raise_error(Error('Interpret', 'Invalid statement'))
        
        self.record = old_record

        if start_id is None:
            return None
        return BlockList((start_id, end_id))

    def visit_Identifier(self, node) -> Variable:
        variable_record = self.record.resolve_variable(node.name)
        return Variable(
            generate_id((variable_record, node.name)),
            variable_record.variable_is_const[node.name]
        )
    
    def visit_VariableDeclaration(self, node) -> None:
        self.record.declare_variable(node.name, node.is_const)
    
    def visit_String(self, node: String):
        return String(node.value)

    def visit_Program(self, node) -> Block:
        event_id = generate_id(node)
        event = self.blocks[event_id] = {
            "opcode": "event_whenflagclicked",
            "next": None,
            "parent": None,
            "inputs": {},
            "fields": {},
            "shadow": False,
            "topLevel": True,
        }
        for statement in node.body:
            block = self.visit(statement)
            if isinstance(block, BlockList):
                # Simple understand: doubly linked lists
                statement_start, statement_end = block.get_start_end()
                self.blocks[statement_start]['parent'] = event_id
                event['next'] = statement_start
                event_id = statement_end
                event = self.blocks[event_id]
            elif block is not None:
                raise_error(Error('Interpret', 'Invalid statement'))
        return Block(event_id)

    def visit_Number(self, node) -> Integer:
        return Integer(node.value)

    def visit_FunctionCall(self, node) -> Block:
        block_id = generate_id(node)
        if node.name not in BLOCK_TYPES:
            raise_error(Error('Interpret', f'Function {node.name} not defined'))
        fields, inputs = {}, {}
        bt = BLOCK_TYPES[node.name]  # block type
        if len(node.args) < len(bt['fields'] + bt['inputs']):
            raise_error(Error('Interpret', f'Too few arguments in function {node.name}'))
        for i in range(len(node.args)):
            arg_node = node.args[i]
            arg = self.visit(arg_node)
            if i < len(bt['fields']):
                if isinstance(arg, Variable):
                    if arg.value[1]:  # is_const
                        raise_error(Error('Interpret', 'Cannot set a constant variable'))
                fields[bt['fields'][i]] = arg.get_id_name()
            elif i < len(bt['fields'] + bt['inputs']):
                arg_name = bt['inputs'][i - len(bt['fields'])]
                if 'STACK' in arg_name:
                    arg_value = arg.get_stack()
                else:
                    arg_value = arg.get_value()
                inputs[arg_name] = arg_value
            else:
                raise_error(Error('Interpret', f'Too many arguments in function {node.name}'))
        self.blocks[block_id] = {
            'opcode': node.name,
            'next': None,
            'parent': None,
            'inputs': inputs,
            'fields': fields,
            'shadow': False,
            'topLevel': False
        }
        return Block(block_id)
