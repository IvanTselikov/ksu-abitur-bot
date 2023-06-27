import os


DEFAULT_APPNAME = 'Безымянный'

APP_PATH = __file__
SRCCODE_PATH = os.path.dirname(APP_PATH) + os.sep

COMPILER_PATH = f'{SRCCODE_PATH}compiler.py'
IMAGE_PATH = f'{SRCCODE_PATH}img{os.sep}'
DEFAULT_BOT_PATH = f'{SRCCODE_PATH}bot{os.sep}'

# путь до хранилища с информацией обо всех модерируемых чатах
STORAGE_PATH = f'{SRCCODE_PATH}groupIDs.json'


# PROJ_PATH = format_dir_path(os.path.abspath(os.path.join(SRCCODE_PATH,'..')))
