# файл предназначен для запуска бота на сервере replit

from project_controller import Project
import config
from flask import Flask
from helper import get_logger
from threading import Thread
import traceback


logger = get_logger('main', need_console_handler=False)
logger.info('main.py запущен.')

try:
    # запуск сервера Flask
    app = Flask('')

    @app.route('/')
    def home():
        try:
            logger.info('Запрос к серверу.')
            if project and project.is_alive():
                response = 'Сервер запущен, бот работает.'
                logger.info(response)
                return response
            else:
                response = 'Бот не отвечает.'
                logger.warning(response)
                return response, 500
        except:
            response = 'Ошибка сервера.'
            logger.error(response)
            logger.error(traceback.format_exc())
            return response, 500


    def run_flask():
        try:
            app.run(host='0.0.0.0', port=80)
        except:
            logger.error(traceback.format_exc())
        finally:
            logger.warning('Сервер Flask остановлен.')

    t = Thread(target=run_flask)
    t.start()


    # запуск бота
    project = Project(config.DEFAULT_BOT_PATH)
    project.run(recompile=True, new_console=False)

    logger.warning('Бот остановлен.')
except:
    logger.error('Ошибка в main.py')
    logger.error(traceback.format_exc())
