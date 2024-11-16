from dataclasses import dataclass
from error import Error, raise_error
from nodes import Block, ListIdentifier, NodeVisitor, FunctionDeclaration
from records import Record
from typing import Optional, Literal
from utils import generate_id
from values import *
import json
import math
import os

def json_with_settings(dump_fn, *args, **kwargs):
    return dump_fn(*args, **kwargs, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

folder = os.path.dirname(__file__)
PRO = 'procedure_'

@dataclass
class Input:
    name: str
    type: Literal['normal', 'boolean', 'block', 'shadow'] = 'normal'
    required: bool = True

SCRATCH_EXTENSION = Literal['music', 'pen', 'videoSensing', 'text2speech', 'translate']

@dataclass
class BlockType:
    inputs: tuple[Input, ...] = ()
    fields: tuple[Input, ...] = ()
    shadow: bool = False
    extensions: tuple[SCRATCH_EXTENSION, ...] = ()

    def __init__(self, inputs: tuple[Input | str, ...]=(), fields: tuple[Input | str, ...]=(), shadow: bool=False, extensions: tuple[SCRATCH_EXTENSION, ...]=()):
        _process = lambda x: tuple(map(lambda y: (Input(y) if not isinstance(y, Input) else y), x))
        self.inputs = _process(inputs)
        self.fields = _process(fields)
        self.shadow = shadow
        self.extensions = extensions
    
    @property
    def required_arguments_count(self):
        _process = lambda x: len(list(filter(lambda y: y.required, x)))
        return _process(self.fields) + _process(self.inputs)

BLOCK_TYPES: dict[str, BlockType] = {
    'control_create_clone_of': BlockType(inputs=(Input(name='CLONE_OPTION', type='shadow'),)),
    'control_create_clone_of_menu': BlockType(fields=('CLONE_OPTION',), shadow=True),
    'control_delete_this_clone': BlockType(),
    'control_if': BlockType(inputs=(Input(name='CONDITION', type='boolean'),
                                    Input(name='SUBSTACK', type='block'))),
    'control_if_else': BlockType(inputs=(Input(name='CONDITION', type='boolean'),
                                         Input(name='SUBSTACK', type='block'),
                                         Input(name='SUBSTACK2', type='block'))),
    'control_repeat': BlockType(inputs=(Input(name='TIMES'),
                                        Input(name='SUBSTACK', type='block'))),
    'control_repeat_until': BlockType(inputs=(Input(name='CONDITION', type='boolean'),
                                              Input(name='SUBSTACK', type='block'))),
    'control_wait': BlockType(inputs=('DURATION',)),
    'data_addtolist': BlockType(inputs=('ITEM',), fields=('LIST',)),
    'data_changevariableby': BlockType(inputs=('VALUE',), fields=('VARIABLE',)),
    'data_deletealloflist': BlockType(fields=('LIST',)),
    'data_deleteoflist': BlockType(inputs=('INDEX',), fields=('LIST',)),
    'data_itemoflist': BlockType(inputs=('INDEX',), fields=('LIST',)),
    'data_lengthoflist': BlockType(fields=('LIST',)),
    'data_replaceitemoflist': BlockType(inputs=('INDEX', 'ITEM'), fields=('LIST',)),
    'data_setvariableto': BlockType(inputs=('VALUE',), fields=('VARIABLE',)),
    'looks_say': BlockType(inputs=('MESSAGE',)),
    'looks_sayforsecs': BlockType(inputs=('MESSAGE', 'SECS')),
    'looks_think': BlockType(inputs=('MESSAGE',)),
    'looks_thinkforsecs': BlockType(inputs=('MESSAGE', 'SECS')),
    'motion_changexby': BlockType(inputs=('DX',)),
    'motion_changeyby': BlockType(inputs=('DY',)),
    'motion_direction': BlockType(),
    'motion_glidesecstoxy': BlockType(inputs=('SECS', 'X', 'Y')),
    'motion_gotoxy': BlockType(inputs=('X', 'Y')),
    'motion_ifonedgebounce': BlockType(),
    'motion_movesteps': BlockType(inputs=('STEPS',)),
    'motion_pointindirection': BlockType(inputs=('DIRECTION',)),
    'motion_setx': BlockType(inputs=('X',)),
    'motion_sety': BlockType(inputs=('Y',)),
    'motion_turnleft': BlockType(inputs=('DEGREES',)),
    'motion_turnright': BlockType(inputs=('DEGREES',)),
    'motion_xposition': BlockType(),
    'motion_yposition': BlockType(),
    'operator_add': BlockType(inputs=('NUM1', 'NUM2')),
    'operator_and': BlockType(inputs=(Input(name='OPERAND1', type='boolean'),
                                      Input(name='OPERAND2', type='boolean'))),
    'operator_contains': BlockType(inputs=('STRING1', 'STRING2')),
    'operator_divide': BlockType(inputs=('NUM1', 'NUM2')),
    'operator_equals': BlockType(inputs=('OPERAND1', 'OPERAND2')),
    'operator_gt': BlockType(inputs=('OPERAND1', 'OPERAND2')),
    'operator_join': BlockType(inputs=('STRING1', 'STRING2')),
    'operator_letter_of': BlockType(inputs=('STRING', 'LETTER')),
    'operator_lt': BlockType(inputs=('OPERAND1', 'OPERAND2')),
    'operator_mod': BlockType(inputs=('NUM1', 'NUM2')),
    'operator_multiply': BlockType(inputs=('NUM1', 'NUM2')),
    'operator_not': BlockType(inputs=(Input(name='OPERAND', type='boolean', required=False),)),
    'operator_or': BlockType(inputs=(Input(name='OPERAND1', type='boolean'),
                                     Input(name='OPERAND2', type='boolean'))),
    'operator_subtract': BlockType(inputs=('NUM1', 'NUM2')),
    'pen_changePenSizeBy': BlockType(inputs=('SIZE',), extensions=('pen',)),
    'pen_clear': BlockType(extensions=('pen',)),
    'pen_penDown': BlockType(extensions=('pen',)),
    'pen_penUp': BlockType(extensions=('pen',)),
    'pen_setPenColorToColor': BlockType(inputs=('COLOR',), extensions=('pen',)),
    'pen_setPenSizeTo': BlockType(inputs=('SIZE',), extensions=('pen',)),
    'pen_stamp': BlockType(extensions=('pen',)),
    'sensing_answer': BlockType(),
    'sensing_askandwait': BlockType(inputs=('QUESTION',)),
    'sensing_loudness': BlockType(),
}

class Interpreter(NodeVisitor):
    def __init__(self) -> None:
        self.record = Record()
        self.project: dict = json.load(open(os.path.join(folder, 'template.json'), encoding='utf-8'))
        self.blocks: dict[str, dict] = self.project['targets'][1]['blocks']
        self.variables: dict[str, list[str]] = self.project['targets'][0]['variables']
        self.lists: dict[str, list[str | list]] = self.project['targets'][0]['lists']
        self.extensions: list[SCRATCH_EXTENSION] = self.project['extensions']
        self.parent_function: Optional[FunctionDeclaration] = None
        self.clone_variable = generate_id(('variable', 'clone', None))
        self.project['targets'][1]['variables'][self.clone_variable] = [self.clone_variable, '[NOT ASSIGNED]']
    
    def visit_Block(self, node) -> BlockList | None:
        if not node.body:
            return NoBlock(None)
        start_id = end_id = None
        event = None

        # Run in new record
        old_record = self.record
        self.record = Record(self.record)
        # If the parent function is not None, add the arguments to the record
        if self.parent_function is not None:
            function_node = self.parent_function
            function_id = generate_id((f'{PRO}name', self.record.resolve_function(function_node.name), function_node.name))
            arg_ids = [generate_id((f'{PRO}argument', function_id, arg_name)) for arg_name in function_node.args]
            for arg_name, arg_id in zip(function_node.args, arg_ids):
                self.record.declare_variable('argument', arg_name, arg_id)
            self.parent_function = None

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
            return NoBlock(None)
        return BlockList((start_id, end_id))

    def visit_Identifier(self, node) -> Variable | Block | String | Number | NoReturn:
        if not self.record.has_variable(node.name):
            if node.name in self.project['targets'][1]['variables']:
                return Variable(node.name, None)
            magic_number = {
                'e': math.e,
                'pi': math.pi,
            }
            special_values = {
                'nan': 'NaN',
                'inf': 'Infinity',
            }
            if node.name in special_values:
                return String(special_values[node.name])
            elif node.name in magic_number:
                return Number(magic_number[node.name])
            raise_error(Error('Interpret', f'Variable {node.name} not declared'))
        
        variable_record = self.record.resolve_variable(node.name)
        variable = variable_record.variables[node.name]
        if variable.type == 'variable':
            return Variable(node.name, variable_record)
        else:  # argument
            # In scratch, it's a function call
            call_id = generate_id(('call', node))
            self.blocks[call_id] = {
                "opcode": "argument_reporter_string_number",
                "next": None,
                # Only return the value, and let external code to set parent
                "parent": None,
                "inputs": {},
                # more=arg_id, because it's only an argument, and not a variable
                "fields": { "VALUE": [variable.more, None] },
                "shadow": False,
                "topLevel": False
            }
            return Block(call_id)
    
    def visit_VariableDeclaration(self, node) -> None:
        self.record.declare_variable('variable', node.name, node.is_const)
        variable_id = generate_id(('variable', node.name, self.record))
        if node.is_array:
            self.lists[variable_id] = [variable_id, []]
        else:
            self.variables[variable_id] = [variable_id, '[NOT ASSIGNED]']
    
    def visit_String(self, node) -> String:
        return String(node.value)

    def visit_Program(self, node) -> Block:
        event_id = generate_id(('event', node))
        event = self.blocks[event_id] = {
            'opcode': 'event_whenflagclicked',
            'next': None,
            'parent': None,
            'inputs': {},
            'fields': {},
            'shadow': False,
            'topLevel': True,
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

    def visit_Number(self, node) -> Number:
        return Number(node.value)

    def visit_FunctionCall(self, node) -> Block:
        if self.record.has_function(node.name):
            return self._visit_custom_FunctionCall(node)
        return self._visit_builtin_FunctionCall(node)

    def _visit_custom_FunctionCall(self, node) -> Block:
        # Custom functions
        call_id = generate_id(('call', node))
        function_node = self.record.resolve_function(node.name).functions[node.name]
        function_id = generate_id((f'{PRO}name', self.record.resolve_function(function_node.name), function_node.name))
        arg_ids = [generate_id((f'{PRO}argument', function_id, arg_name)) for arg_name in function_node.args]

        # mutation
        mutation = {
            'tagName': 'mutation',
            'children': [],
            'proccode': f'{function_id}{" %s" * len(function_node.args)}',
            'argumentids': json_with_settings(json.dumps, arg_ids),
            'warp': 'false'
        }

        if len(node.args) < len(function_node.args):
            raise_error(Error('Interpret', f'Too few arguments in function {function_node.name}'))

        inputs = {}
        for i in range(len(node.args)):
            arg = self.visit(node.args[i])
            if i < len(function_node.args):
                # See _visit_builtin_FunctionCall function
                if isinstance(arg, Block):
                    self.blocks[arg.get_start_end()[0]]['parent'] = call_id
                arg_name = arg_ids[i]
                arg_value = arg.get_as_normal()
                inputs[arg_name] = arg_value
            else:
                raise_error(Error('Interpret', f'Too many arguments in function {node.name}'))
        self.blocks[call_id] = {
            "opcode": "procedures_call",
            "next": None,
            "parent": None,
            "inputs": inputs,
            "fields": {},
            "shadow": False,
            "topLevel": False,
            "mutation": mutation
        }
        return Block(call_id)

    def _visit_builtin_FunctionCall(self, node) -> Block:
        # Built-in functions
        call_id = generate_id(('call', node))
        if node.name not in BLOCK_TYPES:
            # if cannot find the function in built-in functions, raise an error
            raise_error(Error('Interpret', f'Function {node.name} not declared'))
        bt = BLOCK_TYPES[node.name]  # block type
        if len(node.args) < bt.required_arguments_count:
            raise_error(Error('Interpret', f'Too few arguments in function {node.name}'))
        fields, inputs = {}, {}
        for i in range(len(node.args)):
            arg = self.visit(node.args[i])
            if i < len(bt.fields):
                if isinstance(arg, Variable) and arg.value[1] is not None:
                    # Then, by default we think it set the variables
                    # TODO: modify the behavior
                    variable = arg.value[1].variables[arg.value[0]]
                    if variable.type == 'argument':
                        raise_error(Error('Interpret', 'Cannot set an argument variable'))
                    # more=is_const in there, because it's only a variable, and not an argument
                    if variable.more:
                        variable.change_counts += 1
                        # First change: init constant value
                        # Second change: raise an error
                        if variable.change_counts >= 2:
                            raise_error(Error('Interpret', 'Cannot set a constant variable'))
                value = arg.get_as_field()
                fields[bt.fields[i].name] = value
            elif i < len(bt.fields + bt.inputs):
                # Set a block parent
                if isinstance(arg, Block):
                    self.blocks[arg.get_start_end()[0]]['parent'] = call_id

                arg_type = bt.inputs[i - len(bt.fields)]
                if arg_type.type == 'shadow':
                    arg_value = arg.get_as_shadow()
                elif arg_type.type == 'block':
                    arg_value = arg.get_as_block()
                elif arg_type.type == 'normal':
                    arg_value = arg.get_as_normal()
                elif arg_type.type == 'boolean':
                    arg_value = arg.get_as_boolean()
                else:
                    raise ValueError(f'Invalid argument type {arg_type.type}')
                inputs[arg_type.name] = arg_value
            else:
                raise_error(Error('Interpret', f'Too many arguments in function {node.name}'))
        for extension in bt.extensions:
            if extension not in self.extensions:
                self.extensions.append(extension)
        self.blocks[call_id] = {
            'opcode': node.name,
            'next': None,
            'parent': None,
            'inputs': inputs,
            'fields': fields,
            'shadow': bt.shadow,
            'topLevel': False
        }
        return Block(call_id)
    
    def visit_FunctionDeclaration(self, node) -> None:
        # ids
        definition_id = generate_id((f'{PRO}definition', node))
        prototype_id = generate_id((f'{PRO}prototype', node))
        self.record.declare_function(node)
        function_id = generate_id((f'{PRO}name', self.record, node.name))
        arg_ids = [generate_id((f'{PRO}argument', function_id, arg_name)) for arg_name in node.args]

        # mutation
        mutation = {
            'tagName': 'mutation',
            'children': [],
            'proccode': f'{function_id}{" %s" * len(node.args)}',
            'argumentids': json_with_settings(json.dumps, arg_ids),
            'argumentnames':  json_with_settings(json.dumps, arg_ids),
            'argumentdefaults': json_with_settings(json.dumps, ['' * len(node.args)]),
            'warp': 'false'
        }

        # inputs
        inputs = {}
        for arg_id in arg_ids:
            self.blocks[arg_id] = {
                "opcode": "argument_reporter_string_number",
                "next": None,
                "parent": prototype_id,
                "inputs": {},
                "fields": { "VALUE": [arg_id, None] },
                "shadow": True,
                "topLevel": False
            }
            inputs[arg_id] = [1, arg_id]

        # go to inner
        self.parent_function = node
        inner_id = self.visit(node.body).get_start_end()[0]
        if inner_id is not None:
            self.blocks[inner_id]['parent'] = definition_id

        # blocks
        self.blocks[definition_id] = {
            'opcode': 'procedures_definition',
            'next': inner_id,
            'parent': None,
            'inputs': { 'custom_block': [1, prototype_id] },
            'fields': {},
            'shadow': False,
            'topLevel': True,
        }
        self.blocks[prototype_id] = {
            'opcode': 'procedures_prototype',
            "next": None,
            "parent": definition_id,
            "inputs": inputs,
            "fields": {},
            "shadow": True,
            "topLevel": False,
            "mutation": mutation
        }

    def visit_Custom(self, node) -> Custom:
        return Custom(node.name)
    
    def visit_Clone(self, node) -> BlockList | None:
        event_id = generate_id(('event', node))
        event = self.blocks[event_id] = {
            'opcode': 'control_start_as_clone',
            'next': None,
            'parent': None,
            'inputs': {},
            'fields': {},
            'shadow': False,
            'topLevel': True,
        }
        block = self.visit(node.clone)
        # Simple understand: doubly linked lists
        statement_start = block.get_start_end()[0]
        self.blocks[statement_start]['parent'] = event_id
        event['next'] = statement_start
        return self.visit_Block(node._parent)

    def visit_ListIdentifier(self, node) -> ListIdentifier:
        return ListIdentifier(node.name, self.record.resolve_variable(node.name))
