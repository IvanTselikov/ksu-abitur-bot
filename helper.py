import re
import os
import config
from datetime import datetime, timedelta


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


def prepare_text_for_logging(text: str, max_length=50):
    text = text.replace('\n', '\\n')
    return text[:max_length] + '...' if len(text) > max_length else text


def msk_now():
    """Возвращает текущее московское время. Исправляет ошибку, из-за которой в некоторых ОС
    игнорируется смещение часовых поясов при вызове datetime.now().
    """
    msk_now = datetime.now(config.TZ)
    utc_now = datetime.utcnow()

    if msk_now == utc_now:
        msk_now -= timedelta(hours=config.TZ_OFFSET)
    
    return msk_now
