import ast
import uuid
import json

model = json.loads(open('model.json', 'r', encoding='utf-8').read())
tree = ast.parse(open('example.py', 'r', encoding='utf-8').read())

def generate_id():
    return str(uuid.uuid4())

blocks = {}
last_block = None

class Visitor(ast.NodeVisitor):
    def visit_Call(self, node):
        global last_block

        if node.func.id == 'print':
            if last_block is None:
                last_block = generate_id()
                blocks[last_block] = {
                    'opcode': 'event_whenflagclicked',
                    'next': None,
                    'parent': None,
                    'inputs': {},
                    'fields': {},
                    'shadow': False,
                    'topLevel': True,
                }
            parent = last_block
            blocks[parent]['next'] = generate_id()
            last_block = blocks[parent]['next']

            blocks[last_block] = {
                'opcode': 'looks_say',
                'next': None,
                'parent': parent,
                'inputs': { 'MESSAGE': [1, [10, node.args[0].value]] },
                'fields': {},
                'shadow': False,
                'topLevel': False
            }

Visitor().visit(tree)
with open('output.json', 'w', encoding='utf-8') as f:
    model['targets'][1]['blocks'] = blocks
    f.write(json.dumps(model, separators=(',', ':')))
