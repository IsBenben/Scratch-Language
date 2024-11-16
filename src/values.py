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
    type: int | None = None

    @property
    def _type_value(self) -> list:
        real_type = type(self).type
        if real_type is None:
            raise TypeError('Type not defined')
        return [real_type, self.value]

    def get_as_field(self) -> Any:
        raise_error(Error('Value', f'{type(self).__name__} cannot be used as a field'))

    def get_as_boolean(self) -> Any:
        raise_error(Error('Value', f'{type(self).__name__} cannot be used as a boolean'))

    def get_as_block(self) -> Any:
        raise_error(Error('Value', f'{type(self).__name__} cannot be used as a block'))

    def get_as_normal(self) -> Any:
        raise_error(Error('Value', f'{type(self).__name__} cannot be used as a value'))
    
    def get_as_shadow(self) -> Any:
        raise_error(Error('Value', f'{type(self).__name__} cannot be used as a shadow'))

class String(Value):
    value: str
    type = 10

    def get_as_normal(self) -> list:
        return [1, self._type_value]

EMPTY_STRING = String('')

class BlockList(Value):
    value: tuple[str, str]  # (start, end)

    def get_start_end(self) -> tuple:
        return self.value
    
    def get_as_block(self) -> list:
        return [2, self.value[0]]

class NoBlock(BlockList):
    value: None  # type: ignore

    def get_start_end(self) -> tuple[None, None]:
        return (None, None)

    def get_as_block(self) -> NoReturn:
        raise_error(Error('Value', f'{type(self).__name__} cannot be used as a block'))

class Block(BlockList):
    value: str  # type: ignore

    def get_start_end(self) -> tuple:
        return self.value, self.value
    
    def get_as_block(self):
        return [2, self.value]

    def get_as_boolean(self) -> list:
        return [2, self.value]

    def get_as_normal(self) -> list:
        return [3, self.value, EMPTY_STRING._type_value]

    def get_as_shadow(self) -> list:
        return [1, self.value]

class Number(Value):
    value: int | float
    type = 4

    def get_as_normal(self) -> list:
        return [1, self._type_value]
    
class Variable(Value):
    value: tuple[str, Record | None]  # (name, record)
    type = 12

    def __init__(self, name: str, record: Record | None):
        super().__init__((name, record))

    @property
    def _type_value(self) -> list:
        return [type(self).type, self.id, self.id]

    @property
    def id(self) -> str:
        return generate_id(('variable', self.value[0], self.value[1]))

    def get_as_field(self) -> list[str]:
        return [self.id, self.id]

    def get_as_normal(self) -> list:
        return [3, self._type_value, EMPTY_STRING._type_value]

class Custom(Value):
    value: str

    def get_as_field(self) -> list:
        return [self.value, None]

class ListIdentifier(Value):
    value: tuple[str, Record | None]  # (name, record)

    def __init__(self, name: str, record: Record | None):
        super().__init__((name, record))

    @property
    def id(self) -> str:
        return generate_id(('variable', self.value[0], self.value[1]))

    def get_as_field(self) -> list:
        return [self.id, self.id]
