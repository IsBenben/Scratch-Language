from dataclasses import dataclass
from typing import Any, NoReturn
from error import Error, raise_error
from utils import generate_id

@dataclass
class Value:
    value: Any

    def get_value(self) -> Any:
        # See https://en.scratch-wiki.info/wiki/Scratch_File_Format#Blocks
        return self.value

class String(Value):
    value: str

    def get_id_name(self) -> list:
        return [10, self.value]

    def get_value(self) -> list:
        return [1, self.get_id_name()]

EMPTY_STRING = String('')

class BlockList(Value):
    value: tuple  # (start: str, end: str)

    def get_start_end(self) -> tuple:
        return self.value
    
    def get_stack(self):
        return [2, self.value[0]]

    def get_value(self) -> NoReturn:
        raise_error(Error('Value', 'BlockList cannot be used as a value'))

class Block(BlockList):
    value: str

    def get_start_end(self) -> tuple:
        return self.value, self.value
    
    def get_stack(self):
        return [2, self.value]

    def get_value(self) -> list:
        return [3, self.value, EMPTY_STRING.get_id_name()]

class Integer(Value):
    value: int

    def get_value(self) -> list:
        return [1, [4, str(self.value)]]
    
class Variable(Value):
    value: tuple  # (id: str, is_const: bool)

    def __init__(self, id: str, is_const: bool = False):
        super().__init__((id, is_const))

    def get_id_name(self) -> list[str]:
        return [self.value[0], self.value[0]]

    def get_value(self) -> list:
        return [3, [12, self.value[0], self.value[0]], EMPTY_STRING.get_id_name()]
