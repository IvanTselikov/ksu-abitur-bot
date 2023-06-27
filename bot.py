from telebot import TeleBot, types
import json
import time
from datetime import datetime
from threading import Thread
from bot_message import *
from helper import *
import config


class Bot:
    """Класс Telegram-бота со сценарием."""

    # таймаут отправки сообщений
    TIMEOUT = 45


    def __init__(self, token, start_post):
        """Создаёт Telegram-бота с указанным токеном и сценарием.

        Параметры:
        token - токен бота
        start_post - первый пост сценария
        """

        self.bot = TeleBot(token or os.getenv('TOKEN'))
        self.user_table = {}  # таблица с записями вида: "user_id: [post, last_message_id]"
        self.start_post = start_post

        # таблица с записями вида: {chat_id: [start_time, end_time, is_active]}
        # start_time и end_time - два кортежа вида (hour, minute)
        # is_active - флаг: False, если модерация приостановлена
        self.moderated_chats = {}

        if not os.path.exists(config.STORAGE_PATH):
            # создаём файл, если не существует
            with open(config.STORAGE_PATH, 'w'):
                pass
        else:
            # подгружаем информацию о модерируемых чатах из файла
            with open(config.STORAGE_PATH, 'r') as f:
                data = f.read()
                if data:
                    self.moderated_chats = json.loads(data, object_hook=decode_json)
        

        @self.bot.message_handler(commands=['start'])
        def register_new_user(message):
            if message.chat.type == 'private':
                # приватный чат для ответов на вопросы
                # заносим пользователя в таблицу активных пользователей

                # делаем запись о новом игроке или обновляем старую запись
                self.user_table.update({
                    message.from_user.id : [self.start_post, message.id]
                })

                # отправляем первое сообщение
                post = self.start_post
                self.send(message, post)

                while True:
                    post = post.get_next(message.text)
                    if post is None:
                        break
                    self.send(received=message, new_post=post)
                    message.text = None


        @self.bot.message_handler(commands=['moder_on'])
        def moder_on(message):
            """Включает режим тишины в чате по расписанию."""

            if message.chat.type != 'private':
                if self.is_by_admin(message):
                    start_time = None
                    end_time = None

                    if message.chat.id in self.moderated_chats:
                        # чат уже модерировался до этого
                        # извлекаем сохранённые временные границы
                        start_time, end_time, _ = self.moderated_chats[message.chat.id]
                    
                    # извлекаем из сообщения время начала и время окончания, если есть
                    args = message.text.split()[1:]
                    if args:
                        start_time = extract_time(args[0])
                    if len(args) > 1:
                        end_time = extract_time(args[1])
                    
                    if start_time is None or end_time is None:
                        self.bot.send_message(
                            message.chat.id,
                            'Пожалуйста, укажите временные рамки режима тишины в формате чч:мм. Команда:\n/moder_on время_начала время_окончания',
                            timeout=self.TIMEOUT
                        )
                    else:
                        self.update_moderated_chats(
                            chat_id=message.chat.id,
                            start_time=start_time,
                            end_time=end_time,
                            is_active=True
                        )
                        self.bot.send_message(
                            message.chat.id,
                            'Ежедневный режим тишины в чате установлен. '
                                + 'Все сообщения, отправленные с {:02d}:{:02d} до {:02d}:{:02d}, будут удаляться автоматически.\n'.format(
                                    start_time[0], start_time[1], end_time[0], end_time[1])
                                + 'Для изменения временных рамок используйте команду повторно с другими параметрами.\n'
                                + 'Для отключения режима тишины воспользуйтесь командой /moder_off.\n',
                                timeout=self.TIMEOUT
                        )
                else:
                    # если команду ввёл не администратор, сообщение удаляется
                    self.bot.delete_message(message.chat.id, message.id)
            else:
                # в приватном чате команда обрабатывается как обычный текст
                handle_other(message)


        @self.bot.message_handler(commands=['moder_off'])
        def moder_off(message):
            """Отключает режим тишины в чате."""

            if message.chat.type != 'private':
                if self.is_by_admin(message):
                    if message.chat.id in self.moderated_chats:
                        self.update_moderated_chats(chat_id=message.chat.id, is_active=False)
                        self.bot.send_message(
                            message.chat.id,
                            'Режим тишины отключён. Чтобы вновь его активировать, введите команду:\n/moder_on время_начала время_окончания (формат времени - чч:мм).',
                            parse_mode='HTML',
                            timeout=self.TIMEOUT
                        )
                    else:
                        self.bot.send_message(
                            message.chat.id,
                            'Режим тишины ещё не активирован в этом чате. Для его активации введите команду:\n/moder_on время_начала время_окончания (формат времени - чч:мм).',
                            parse_mode='HTML',
                            timeout=self.TIMEOUT
                        )
                else:
                    # если команду ввёл не администратор, сообщение удаляется
                    self.bot.delete_message(message.chat.id, message.id)
            else:
                # в приватном чате команда обрабатывается как обычный текст
                handle_other(message)
        

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_buttons(call):
            """Обрабатывает нажатия на кнопки."""
            self.bot.answer_callback_query(call.id)

            if call.message.chat.type == 'private':
                if call.from_user.id in self.user_table:
                    post, last_message_id = self.user_table[call.from_user.id]

                    if last_message_id == call.message.id:
                        while True:
                            # получаем новые сообщения для отправки
                            post = post.get_next(call.data)
                            if post is None:
                                # сообщения кончились либо ожидается ответ от пользователя
                                break
                            self.send(received=call.message, new_post=post)
                            call.data = None
                else:
                    # пользователь ещё не нажал на "Старт" (например, нажал на кнопки,
                    # пришедшие до перезапуска бота на сервере)
                    self.bot.send_message(
                        call.message.chat.id,
                        'Пожалуйста, перезапустите бота, введя команду /start',
                        timeout=self.TIMEOUT
                    )
                
                # удаление старых кнопок
                # time.sleep(0.5)
                # self.bot.delete_message(call.message.chat.id, call.message.id)


        @self.bot.message_handler(content_types=[
            'audio', 'photo', 'voice', 'video', 'document',
            'text', 'location', 'contact', 'sticker'
        ])
        def handle_other(message):
            """Обрабатывает сообщения от пользователя (всё, кроме кнопок)."""

            if message.chat.type == 'private':
                # при получении сообщения от пользователя ему снова отправляются
                # последние кнопки

                if message.from_user.id in self.user_table:
                    last_post, last_message_id = self.user_table[message.from_user.id]
                    self.send(received=message, new_post=last_post)

                    # удаляем старые кнопки
                    # time.sleep(0.5)
                    # self.bot.delete_message(message.chat.id, last_message_id)
                else:
                    # пользователь ещё не начал диалог -> отправляем первый пост
                    register_new_user(message)
            else:
                # удаление сообщений, отправленных во время режима тишины
                if message.chat.id in self.moderated_chats:
                    (start_hour, start_minute), (end_hour,end_minute), is_active = self.moderated_chats[message.chat.id]
                    if is_active:
                        # проверяем, отправлено ли сообщение во время режима тишины
                        dt = datetime.fromtimestamp(message.date).timetuple()
                        hour, minute = dt.tm_hour, dt.tm_min

                        ts_now = 60 * hour + minute
                        ts_start = 60 * start_hour + start_minute
                        ts_end = 60 * end_hour + end_minute

                        if ts_start < ts_end:
                            # временной интервал внутри одного дня
                            is_silence_now = (ts_now >= ts_start and ts_now < ts_end)
                        else:
                            # временной интервал включает переход через полночь
                            is_silence_now = (ts_now >= ts_start or ts_now < ts_end)

                        if is_silence_now:
                            self.bot.delete_message(message.chat.id, message.message_id)
    

    def _shedule_loop(self):
        # каждую минуту процедура ищет чаты, в которых в эту минуту по расписанию
        # начинается режим тишины, и отправляет сообщение о начале режима тишины
        # в эти чаты

        while True:
            # вычисляем время до начала очередной минуты, и засыпаем на это время
            sec_delta = 60 - datetime.now().second
            time.sleep(sec_delta)

            hour = datetime.now().hour
            minute = datetime.now().minute

            for chat_id in self.moderated_chats:
                (start_hour, start_minute), (end_hour,end_minute), is_active = self.moderated_chats[chat_id]
                if is_active:
                    if hour == start_hour and minute == start_minute:
                        self.bot.send_message(
                            chat_id,
                            text="🤫 Режим тишины в чате. Сообщения в период с {:02d}:{:02d} до {:02d}:{:02d} будут автоматически удаляться.".format(
                                start_hour, start_minute, end_hour, end_minute
                            ),
                            timeout=self.TIMEOUT
                        )
        

    def start(self):
        """Запускает бота в текущем потоке."""
        
        # запускаем цикл расписания в отдельном потоке
        new_thread = Thread(target=self._shedule_loop)
        new_thread.start()

        # начинаем слушать бота
        self.bot.infinity_polling(timeout=self.TIMEOUT)


    def stop(self):
        """Останавливает бота."""
        self.bot.stop_bot()
    

    def is_alive(self):
        """Возвращает True, если бот запущен в данный момент."""
        return self.bot.get_me()


    def send(self, received, new_post):
        """Отправляет пост в чат.

        Параметры:
        received - полученнное сообщение (тип telebot.Message)
        new_post - пост для отправки (тип bot_message.Post)
        """
        if isinstance(new_post, TextPost):
            sent = self.bot.send_message(received.chat.id, new_post.content, timeout=self.TIMEOUT, parse_mode='HTML')
        elif isinstance(new_post, ImagePost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_photo(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, VideoPost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_video(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, VoicePost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_voice(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, GifPost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_animation(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, DocPost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_document(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, AudioPost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_audio(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, StickerPost):
            with open(new_post.content, 'rb') as content:
                sent = self.bot.send_sticker(received.chat.id, content, timeout=self.TIMEOUT)
        elif isinstance(new_post, ButtonsPost):
            markup_inline = types.InlineKeyboardMarkup()
            for button in new_post.content:
                new_item = types.InlineKeyboardButton(text=button.text,
                                                      callback_data=button.callback_data)
                markup_inline.add(new_item)
            sent = self.bot.send_message(received.chat.id, new_post.caption,
                                           reply_markup=markup_inline, timeout=self.TIMEOUT,
                                           parse_mode='HTML')
        elif isinstance(new_post, GroupPost):
            if not new_post.content:  # сгруппированное сообщение содержит только текст
                sent = self.bot.send_message(
                    received.chat.id, new_post.caption, timeout=self.TIMEOUT
                )
            else:
                medias = []
                opened_files = []
                for post in new_post.content:
                    content = open(post.content, 'rb')
                    if isinstance(post, DocPost):
                        medias = [types.InputMediaDocument(content)]
                        break
                    elif isinstance(post, AudioPost):
                        medias= [types.InputMediaAudio(content)]
                        break
                    elif isinstance(post, ImagePost):
                        medias.append(types.InputMediaPhoto(content))
                    elif isinstance(post, VideoPost):
                        medias.append(types.InputMediaVideo(content))
                    opened_files.append(content)
                medias[0].caption = new_post.caption
                sent = self.bot.send_media_group(received.chat.id, medias, timeout=self.TIMEOUT)[-1]
                for file in opened_files:
                    file.close()
        else:
            sent = None
            print('Неизвестный тип сообщений.')
        
        # сохраняем id последнего отправленного сообщения для конкретного пользователя и новый пост
        self.user_table.update({ received.chat.id : [new_post, sent.id] })

        if new_post.is_endpoint():
            # отправлено последнее сообщение сценария, пользователь удаляется из списка активных
            self.user_table.pop(received.chat.id)
    

    def is_by_admin(self, message):
        """Возвращает True, если указанное сообщение отправлено администратором или владельцем чата."""
        user_status = self.bot.get_chat_member(message.chat.id, message.from_user.id).status
        return user_status == 'administrator' or user_status == 'creator'
    

    def update_moderated_chats(self, chat_id, start_time=None, end_time=None, is_active=None):
        self.moderated_chats.update({ chat_id: [
            start_time or self.moderated_chats[chat_id][0],
            end_time or self.moderated_chats[chat_id][1],
            is_active if is_active is not None else self.moderated_chats[chat_id][2]
        ] })

        # записываем обновлённую информацию в файл
        with open(config.STORAGE_PATH, 'w') as f:
            json.dump(self.moderated_chats, f)
    

    def remove_moderated_chat(self, chat_id):
        self.moderated_chats.pop(chat_id)

        # записываем обновлённую информацию в файл
        with open(config.STORAGE_PATH, 'w') as f:
            json.dump(self.moderated_chats, f)
