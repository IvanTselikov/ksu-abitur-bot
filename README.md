# Telegram-бот для абитуриентов Костромского государственного университета

### Функционал
1. Ответы на часто задаваемые вопросы в личной переписке с ботом;
2. Установка и настройка режима тишины (ежедневное автоматическое удаление новых сообщений за определённый период времени) в групповом чате, с оповещением о начале этого режима.

Для развёртывания бота на сервере необходимо знать токен бота, для общения с ботом нужен его юзернейм (начинается с @).


### Требования к серверу
Требования к серверу:
* ОС Linux, Windows;
* Доступ в Интернет;
* Установлен интерпретатор Python версии 3.10 или выше;
* Установлен пакетный менеджер pip (pip3 в Linux);
* 512 Мб ОЗУ;
* 1 Гб ПЗУ.


Чтобы запустить бота на сервере, необходимо:
1. Скачать и распаковать архив с проектом либо склонировать репозиторий;
2. В файле *token.py* прописать токен бота;
3. Перейти в папку с проектом и выполнить следующие команды:
	* Для Windows:
		* `python -m venv venv` (создание виртуальной среды);
		* `venv\Scripts\activate` (активация виртуальной среды);
		* `pip install -r requirements.txt` (установка необходимых пакетов);
		* `python main.py -c` (компиляция сценария и запуск бота).
	* Для Linux:
		* `python3 -m venv venv`
		* `source venv/bin/activate`
		* `pip3 install -r requirements.txt`
		* `python main.py -c`

В дальнейшем, чтобы запустить проект, достаточно будет выполнить следующие команды:
* Для Windows:
	* `venv\Scripts\activate`
	* `python main.py`
* Для Linux:
	* `source venv/bin/activate`
	* `python main.py`

Остановить бота можно по Ctrl+C.


### Начало работы с ботом в Telegram
Чтобы начать личную переписку с ботом, достаточно кликнуть на его юзернейм в Telegram, затем нажать кнопку Start.

Чтобы использовать бота в целях модерации группы, необходимо:
1. Пригласить бота в группу;
2. Назначить его администратором (функция доступна в мобильной версии Telegram: нужно найти бота в списке пользователей чата, нажать и удерживать, выбрать опцию "Promote to admin");
3. Включить режим тишины и установить его временные рамки командой `/moder_on время_начала время_окончания` (команду можно отправить как обычное сообщение в чат), формат времени - чч:мм, время московское.

Управление режимом тишины:
* Отключить режим тишины можно с помощью команды `/moder_off`;
* Вновь активировать ранее отключенный режим тишины (с теми же временными рамками) можно с помощью команды `/moder_on` (без параметров);
* Изменить временные рамки - снова использовать полную версию команды (`/moder_on время_начала время_окончания`);
* Изменить только время начала - команда `/moder_on время_начала`.
