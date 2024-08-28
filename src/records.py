from __future__ import annotations
from error import raise_error, Error
from typing import Optional
from dataclasses import dataclass
from typing import Any
from utils import generate_id

class Record:
    def __init__(self, parent: Optional[Record] = None):
        self.parent = parent
        self.variables = set()  # the variable names is its hash
        self.variable_is_const = {}
    
    def declare_variable(self, name: str, is_const: bool = False) -> None:
        if name in self.variables:
            raise_error(Error('Record', f'Variable "{name}" already declared'))
        self.variables.add(name)
        self.variable_is_const[name] = is_const

    def resolve_variable(self, name: str) -> Record:
        if name in self.variables:
            return self
        if self.parent is not None:
            return self.parent.resolve_variable(name)
        raise_error(Error('Record', f'Variable "{name}" not declared'))
