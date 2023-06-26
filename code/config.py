import sys
import os

DEFAULT_APPNAME = 'Безымянный'

IS_EXE = getattr(sys, 'frozen', False)
if IS_EXE:
    APP_PATH = sys.executable
    SRCCODE_PATH = os.path.abspath(os.path.join(APP_PATH,'../../..')) + os.sep
    COMPILER_PATH = f'{SRCCODE_PATH}dist{os.sep}compiler{os.sep}compiler.exe'
else:
    APP_PATH = __file__
    SRCCODE_PATH = os.path.dirname(APP_PATH) + os.sep
    COMPILER_PATH = f'{SRCCODE_PATH}compiler.py'

PROJ_PATH = os.path.abspath(os.path.join(SRCCODE_PATH,'..')) + os.sep
HTML_PATH = f'{PROJ_PATH}html{os.sep}'
IMAGE_PATH = f'{PROJ_PATH}img{os.sep}'

DEFAULT_BOT_PATH = f'{PROJ_PATH}bot{os.sep}'


# путь до хранилища с информацией обо всех модерируемых чатах
STORAGE_PATH = f'{PROJ_PATH}groupIDs.json'
