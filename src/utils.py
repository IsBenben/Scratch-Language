from typing import Any

valid_chars = '_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$'
target_ids: dict[int, Any] = {}

def generate_id(target: Any) -> str:
    id_num = hash(target) + 9223372036854775809
    while id_num in target_ids and target_ids[id_num] != target:
        id_num += 1
    res = ''
    while id_num > 0:
        res = valid_chars[id_num % len(valid_chars)] + res
        id_num //= len(valid_chars)
    target_ids[id_num] = target
    return res
