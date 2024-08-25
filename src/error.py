from dataclasses import dataclass
import sys
from typing import NoReturn

@dataclass
class Error:
    type: str
    msg: str

def raise_error(error: Error) -> NoReturn:
    print('[ERROR!] {}: {}'.format(error.type, error.msg))
    sys.exit()
