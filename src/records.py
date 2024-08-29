from __future__ import annotations
from dataclasses import dataclass
from error import raise_error, Error
from nodes import FunctionDeclaration
from typing import Optional, Literal

VariableType = Literal['variable', 'argument']

@dataclass
class Variable:
    type: VariableType
    name: str
    # type of "more":
    #   bool if type == 'variable'
    #   str if type == 'argument'
    more: bool | str
    # change_counts:
    #   the variable change counts
    #   argument cannot change, so it's always 0
    change_counts: int

class Record:
    def __init__(self, parent: Optional[Record] = None):
        self.parent = parent
        self.variables: dict[str, Variable] = {}
        self.functions: dict[str, FunctionDeclaration] = {}  # the function names is its hash
    
    def declare_variable(self, type: VariableType, name: str, more: bool | str) -> None:
        # Overrides function arguments, but not variables
        # Overrides variables declaration is forbidden
        if name in self.variables and self.variables[name].type == 'variable':
            raise_error(Error('Record', f'Variable "{name}" already declared'))
        if name in self.functions:
            raise_error(Error('Record', f'Variable "{name}" conflicts with function'))
        # The information of variable node less than Variable data class
        self.variables[name] = (Variable(type, name, more, 0))
    
    def declare_function(self, node: FunctionDeclaration) -> None:
        name = node.name
        if name in self.functions:
            raise_error(Error('Record', f'Function "{name}" already declared'))
        if name in self.variables:
            raise_error(Error('Record', f'Function "{name}" conflicts with variable'))
        # Known the node, then known the information of the function
        self.functions[name] = node

    def resolve_variable(self, name: str) -> Record:
        # The resolve functions return the record where the variable is declared
        if name in self.variables:
            return self
        if self.parent is not None:
            return self.parent.resolve_variable(name)
        raise_error(Error('Record', f'Variable "{name}" not declared'))
    
    def has_function(self, name: str) -> bool:
        # Try find the function, if found, return True, else return False
        if name in self.functions:
            return True
        if self.parent is not None:
            return self.parent.has_function(name)
        return False
    
    def resolve_function(self, name: str) -> Record:
        if name in self.functions:
            return self
        if self.parent is not None:
            return self.parent.resolve_function(name)
        raise_error(Error('Record', f'Function "{name}" not declared'))
