import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import config


if not os.path.exists(config.LOGS_DIR):
    os.makedirs(config.LOGS_DIR)

logging.raiseExceptions = False


def _namer(default_name):
    base_filename, ext, date = default_name.split('.')
    return '.'.join([base_filename, date, ext])


def get_logger(
        name,
        base_logger=None,
        level=logging.INFO,
        stream=sys.stdout,
        fmt=config.LOGS_FMT,
        need_console_handler=True,
        need_file_handler=True
    ):
    logger = base_logger or logging.getLogger(name)
    logger.setLevel(level)

    if need_console_handler:
        console_handler = logging.StreamHandler(stream)
        console_handler.setFormatter(logging.Formatter(fmt=fmt))
        logger.addHandler(console_handler)

    if need_file_handler:
        files_handler = TimedRotatingFileHandler(
            filename='{}{}.{}'.format(config.LOGS_DIR, name, config.LOGS_EXTENSION),
            **config.LOGS_INTERVAL
        )
        files_handler.namer = _namer
        files_handler.setFormatter(logging.Formatter(fmt=fmt))
        logger.addHandler(files_handler)

    return logger
