# *-* encoding: utf-8 *-*
"""
Copyright (c) Copyright 2024 Scratch-Language Developers
https://github.com/IsBenben/Scratch-Language
License under the Apache License, version 2.0
"""

# Some utilities for create Scratch blocks

from nodes import *
from typing import overload, NoReturn
from error import *

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

@overload
def poly_copy_list(*, from_: ListIdentifier, to: ListIdentifier, index: Identifier) -> Block: ...  # type: ignore[overload-overlap]
@overload
def poly_copy_list(*, from_: Expression, to: ListIdentifier, index: Identifier) -> NoReturn: ...
@overload
def poly_copy_list(*, from_: ListIdentifier, to: Identifier, index: Identifier) -> NoReturn: ...
@overload
def poly_copy_list(*, from_: Expression, to: Identifier, index: Identifier) -> Statement: ...

def poly_copy_list(*, from_, to, index):  # type: ignore
    is_array = isinstance(from_, ListIdentifier)
    if is_array != isinstance(to, ListIdentifier):
        raise_error(Error('Poly', 'Cannot copy to the variable because the types are different'))
    if not is_array:
        return FunctionCall('data_setvariableto', [from_, to])
    else:
        # # Pseudo Code:
        # index = 0
        # identifier.clear()
        # while index < len(expression):
        #     identifier.append(expression[index])
        return Block([
            FunctionCall('data_deletealloflist', [to]),
            FunctionCall('data_setvariableto', [index, Number(0)]),
            FunctionCall('control_repeat', [
                FunctionCall('data_lengthoflist', [from_]),
                Block([
                    FunctionCall('data_changevariableby', [index, Number(1)]),
                    FunctionCall('data_addtolist', [to, FunctionCall('data_itemoflist', [from_, index])])
                ])
            ]),
        ])

def poly_filter_non_declaration(body: Block) -> Block:
    return Block([
        statement
        for statement in body.body
        if not isinstance(statement, (VariableDeclaration, FunctionDeclaration))
    ])
