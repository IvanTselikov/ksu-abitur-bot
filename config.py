import os
import pytz
from bot_token import TOKEN


os.environ['TOKEN'] = TOKEN


DEFAULT_APPNAME = 'Безымянный'

APP_PATH = __file__
SRCCODE_PATH = os.path.dirname(APP_PATH) + os.sep

MAIN_PATH = f'{SRCCODE_PATH}main.py'
IMAGE_PATH = f'{SRCCODE_PATH}img{os.sep}'
DEFAULT_BOT_PATH = f'{SRCCODE_PATH}bot{os.sep}'

# путь до хранилища с информацией обо всех модерируемых чатах
STORAGE_PATH = f'{SRCCODE_PATH}groupIDs.json'

TZINFO = 'Europe/Moscow'  # московское время
TZ = pytz.timezone(TZINFO)

LOGS_DIR = SRCCODE_PATH + 'logs' + os.sep
LOGS_INTERVAL = {
    'when': 'D',
    'interval': 1,
    'backupCount': 2
}
LOGS_DEFAULT_NAME = 'logs'  # название файла с архивированнными логами
LOGS_DATA_SEP = ' | '
LOGS_FMT = LOGS_DATA_SEP.join(
    ['%(asctime)s', '%(levelname)s', '%(name)s', '%(message)s']
)
LOGS_DATEFMT = '%Y-%m-%d %H:%M:%S,%f'
LOGS_EXTENSION = 'log'


# PROJ_PATH = format_dir_path(os.path.abspath(os.path.join(SRCCODE_PATH,'..')))
