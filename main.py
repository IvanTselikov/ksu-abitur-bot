# файл предназначен для запуска бота на сервере replit

from project_controller import Project
import config
from flask import Flask


# запуск бота
project = Project(config.DEFAULT_BOT_PATH)
project.run(recompile=False, new_console=False)

# запуск сервера Flask
app = Flask('')

@app.route('/')
def home():
    if project and project.is_alive():
        return 'Сервер запущен, бот работает.'
    else:
        return 'Бот не отвечает.'

app.run(host='0.0.0.0', port=80)
