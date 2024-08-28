from typing import Any

valid_chars = '_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def generate_id(target: Any) -> str:
    id_num = abs(hash(target))
    res = ''
    while id_num > 0:
        res = valid_chars[id_num % len(valid_chars)] + res
        id_num //= len(valid_chars)
    return res
