from dataclasses import dataclass
from typing import NoReturn

@dataclass
class Error:
    type: str
    msg: str

class ScratchLanguageError(Exception):
    pass

def raise_error(error: Error) -> NoReturn:
    print('[ERROR!] {}: {}'.format(error.type, error.msg))
    raise ScratchLanguageError(error.msg)
