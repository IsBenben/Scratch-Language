# *-* encoding: utf-8 *-*
"""
Copyright (c) Copyright 2024 Scratch-Language Developers
https://github.com/IsBenben/Scratch-Language
License under the Apache License, version 2.0
"""

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
