from dataclasses import dataclass
from typing import Any, NoReturn
from error import Error, raise_error
from records import Record
from utils import generate_id

# See for more information:
# https://en.scratch-wiki.info/wiki/Scratch_File_Format#Blocks

@dataclass
class Value:
    value: Any

    def get_value(self) -> Any:
        return self.value

class String(Value):
    value: str

    def get_id_name(self) -> list:
        return [10, self.value]

    def get_value(self) -> list:
        return [1, self.get_id_name()]

EMPTY_STRING = String('')

class BlockList(Value):
    value: tuple[str, str]  # (start, end)

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
    value: tuple[str, Record]  # (name, record)

    def __init__(self, name: str, record: Record):
        super().__init__((name, record))

    @property
    def id(self) -> str:
        return generate_id(('variable', self.value[0], self.value[1]))

    def get_id_name(self) -> list[str]:
        return [self.id, self.id]

    def get_value(self) -> list:
        return [3, [12, self.id, self.id], EMPTY_STRING.get_id_name()]
