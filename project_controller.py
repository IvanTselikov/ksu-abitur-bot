import os
import shutil
import pickle
import subprocess
import sys
from bot import Bot
from code_analyzer import CodeAnalyzer
from helper import *
import bot_parser
import config
import traceback
from app_logging import get_logger
from wakepy import keep


class Project:
    """Проект с ботом."""

    RES_NAME = 'res'  # название папки с ресурсами
    BIN_NAME = 'bin'  # название папки со скомпилированным проектом
    SCN_FILENAME = 'code.scn'  # название файла с кодом
    OBJ_FILENAME = 'obj.bin'  # название файла со скомпилированными объектами

    def __init__(self, path):
        """Создаёт новый проект по указанному пути."""
        self.path = format_dir_path(path)  # путь до проекта
        self.res = self.path + self.RES_NAME  # путь до папки с ресурсами
        self.scn = self.path + self.SCN_FILENAME  # путь до файла с кодом
        self.bin = self.path + self.BIN_NAME  # путь до папки со скомпилированным проектом
        self.obj = self.bin + os.sep + self.OBJ_FILENAME  # путь до файла со скомпилированными объектами
        self.name = os.path.basename(path)  # название проекта
        self.code_analyzer = CodeAnalyzer()
        self.process = None  # процесс, в котором запущен бот (если запущен в новом терминале)
        self.bot = None  # бот (если запущен в текущем терминале)
        self.logger = get_logger('project_controller')
        self.create_temp()


    def create_temp(self):
        """Создаёт файловую структуру проекта."""
        if not os.path.isdir(self.res):
            # создаём папку с ресурсами
            os.makedirs(self.res)
        if not os.path.isdir(self.bin):
            # создаём папку с объектами
            os.mkdir(self.bin)
            # создаём файл для скомпилированных объектов
            with open(self.obj, 'w') as f:
                pass
        if not os.path.isfile(self.scn):
            # создаём файл с кодом
            with open(self.scn, 'w', encoding='utf-8', newline='') as f:
                pass


    def save(self, code):
        """Сохраняет код в файле для кода в проекте.

        Параметры:
        code - код для сохранения
        """
        try:
            with open(self.scn, 'w', encoding='utf-8', newline='') as f:
                f.write(code)
        except:
            # файл с кодом был затёрт
            self.create_temp()  # восстанавливаем структуру проекта
            self.name = os.path.basename(self.path)
            with open(self.scn, 'w', encoding='utf-8', newline='') as f:
                f.write(code)


    def is_saved(self, current_code):
        """Возвращает True, если указанный код сохранён в проекте."""
        try:
            with open(self.scn, 'r', encoding='utf-8', newline='') as f:
                saved_code = f.read()
                return current_code == saved_code
        except:
            # не удалось открыть файл с сохранённым кодом
            return False


    def get_code(self):
        """ Возвращает сохранённый код проекта."""
        try:
            with open(self.scn, 'r', encoding='utf-8', newline='') as f:
                return f.read()
        except:
            # не удалось открыть файл с сохранённым кодом
            return ''


    def is_project(path):
        """ Проверяет файловую структуру в папке на соответствие файловой структуре проекта.

        Параметры:
        path - папка для проверки
        """
        if os.path.isdir(path + os.sep + Project.RES_NAME) and\
           os.path.isfile(path + os.sep + Project.SCN_FILENAME) and\
           os.path.isfile(path + os.sep + Project.BIN_NAME + os.sep + Project.OBJ_FILENAME):
            return True
        return False


    def get_resources_names(self):
        """Возвращает названия файлов в каталоге ресурсов."""
        if os.path.isdir(self.res):
            return os.listdir(self.res)
        return []


    def add_res(self, path):
        """Добавляет файл ресурсов в проект."""
        shutil.copy(path, self.res)


    def remove_res(self, name):
        """Удаляет файл ресурсов из проекта."""
        os.remove(self.res + os.sep + name)

    
    def _runner(self, recompile):
        try:
            if recompile:
                code = self.get_code()
                analyzed, _ = self.code_analyzer.get_words(code)
                words_for_parsing = self.code_analyzer.get_words_for_parsing(analyzed)
                scenery = bot_parser.getScenery(words_for_parsing, self.res + os.sep)
                serialized = pickle.dumps(scenery)
                with open(self.obj, 'wb') as f:
                    f.write(serialized)
            self.logger.info('Начат запуск бота.')
            with open(self.obj, 'rb') as f:
                token, first_message = pickle.load(f)
            self.bot = Bot(token, first_message)
            self.logger.info('Бот запущен. Для его остановки нажмите Ctrl+C.')

            try:
                with keep.running() as m:  # не даём боту уснуть
                    self.bot.start()
            except:
                # wakepy работает не на всех ОС
                self.bot.start()
        except bot_parser.BotParsingException as e:
            self.logger.error('Ошибка в сценарии бота: ' + str(e))
        except Exception as e:
            self.logger.error(traceback.format_exc())


    def run(self, recompile, new_console=True):
        """Запускает бота."""
        if new_console:
            # запускаем бота в новой консоли
            args = ['python', config.MAIN_PATH, self.path]
            if recompile:
                args.insert(2, '-c')
            self.process = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # # запускаем бота в текущей консоли в новом потоке
            # t = threading.Thread(target=self._runner, args=[recompile])
            # t.start()

            self._runner(recompile)


    def stop(self):
        """Останавливает бота."""
        if self.process:
            # закрываем консоль
            self.process.kill()
            self.process = None
        elif self.bot.is_alive():
            # останавливаем поток, слушающий бота
            self.bot.stop()
            self.bot = None


    def is_alive(self):
        try:
            return (self.process and self.process.poll() is None)\
                or (self.bot and self.bot.is_alive())
        except:
            return False



# создание проекта по указанному пути
if __name__ == '__main__':
    path = sys.argv[1]
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            print('Некорректный путь: {}'.format(path))
    if os.path.isdir(path):
        if not Project.is_project(path):
            project = Project(path)
            print('Проект "{}" успешно создан!'.format(project.name))
        else:
            print('В папке "{}" уже создан проект.'.format(path))
