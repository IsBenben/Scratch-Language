# Some utilities for create scratch blocks

from nodes import *

def poly_concat_blocks(*blocks: Block):
    return Block(sum((block.body for block in blocks), start=[]))

def poly_foreach(*, var: Identifier, index: Identifier, sequence: ListIdentifier, body: Block) -> list[Statement]:
    return [
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
    ]
