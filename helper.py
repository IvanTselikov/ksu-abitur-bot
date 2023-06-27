import re
import os


time_pattern = re.compile('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')


def decode_json(o):
    """Переводит все строки в json-объекте в числа, если это возможно."""
    if isinstance(o, str):
        try:
            return int(o)
        except ValueError:
            return o
    elif isinstance(o, dict):
        return {decode_json(k): decode_json(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [decode_json(v) for v in o]
    else:
        return o


def extract_time(time):
    """Возвращает кортеж (hour, minute) из строки формата hh:mm, или None,
    если переданная строка имела неверный формат."""

    return tuple(map(int, time.split(':'))) if time_pattern.match(time) else None


def format_dir_path(path):
    return path if path.endswith(os.sep) else path + os.sep
