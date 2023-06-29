import re
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import config


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


def get_logger(
        name,
        base_logger=None,
        level=logging.INFO,
        stream=sys.stdout,
        fmt=u'%(asctime)s | %(levelname)s | %(message)s',
        need_console_handler=True,
        need_file_handler=True
    ):
    if not os.path.exists(config.LOGS_DIR):
        os.makedirs(config.LOGS_DIR)

    logging.raiseExceptions = False

    logger = base_logger or logging.getLogger(name)
    logger.setLevel(level)

    if need_console_handler:
        console_handler = logging.StreamHandler(stream)
        console_handler.setFormatter(logging.Formatter(fmt=fmt))
        
        logger.addHandler(console_handler)

    if need_file_handler:
        files_handler = TimedRotatingFileHandler(
            filename='{}{}.log'.format(config.LOGS_DIR, name),
            **config.LOGS_INTERVAL
        )
        files_handler.setFormatter(logging.Formatter(fmt=fmt))
        logger.addHandler(files_handler)

    return logger


def prepare_text_for_logging(text: str, max_length=75):
    text = text.replace('\n', '\\n')
    return text[:max_length] + '...' if len(text) > max_length else text
