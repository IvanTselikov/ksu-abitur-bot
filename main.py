# файл предназначен для запуска бота на сервере replit

from project_controller import Project
import config
from flask import Flask
from helper import get_logger
from threading import Thread
import traceback


logger = get_logger('main', need_console_handler=False)

try:
    # запуск сервера Flask
    app = Flask('')

    @app.route('/')
    def home():
        logger.info('Запрос к серверу.')
        if project and project.is_alive():
            response = 'Сервер запущен, бот работает.'
            logger.info(response)
            return response
        else:
            response = 'Бот не отвечает.'
            logger.error(response)
            return response, 500

    def run_flask():
        app.run(host='0.0.0.0', port=80)

    t = Thread(target=run_flask)
    t.start()


    # запуск бота
    project = Project(config.DEFAULT_BOT_PATH)
    project.run(recompile=True, new_console=False)
except:
    logger.error(traceback.format_exc())
