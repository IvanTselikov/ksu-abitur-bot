import telebot
from telebot import TeleBot, types
import json
import time
from datetime import datetime
from threading import Thread
import logging
from bot_message import *
from helper import decode_json, extract_time, prepare_text_for_logging
from app_logging import get_logger
import config
import traceback


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
        self.is_alive = False

        # настройка логгера TeleBot
        telebot.logger.handlers.clear()

        telebot_logger = get_logger(
            'telebot_errors',
            base_logger=telebot.logger,
            level=logging.ERROR
        )

        # не выводим stacktrace ошибки в консоль, записываем только в файл
        console_handler = next(
            h for h in telebot_logger.handlers if isinstance(h, logging.StreamHandler)
        )
        console_handler.addFilter(lambda record: not record.getMessage().startswith('Exception traceback:'))

        self.logger = get_logger('bot')


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

                self.logger.info('Пользователь {} ({}) начал общение с ботом.'.format(
                    message.from_user.id,
                    message.from_user.username,
                ))
                                
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
                self.logger.info('Группа {} - отправлена команда "{}" пользователем {} ({}) ({})'.format(
                    message.chat.id,
                    prepare_text_for_logging(message.text),
                    message.from_user.id,
                    message.from_user.username,
                    'админ или создатель чата' if self.is_by_admin(message) else 'не адмим'
                ))
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
                        sent = self.bot.send_message(
                            message.chat.id,
                            'Пожалуйста, укажите временные рамки режима тишины в формате чч:мм (время московское). Команда:\n/moder_on время_начала время_окончания',
                            timeout=self.TIMEOUT
                        )
                        self.logger.info('Отправлено сообщение в группу {}: "{}".'.format(
                            sent.chat.id,
                            prepare_text_for_logging(sent.text)
                        ))
                    else:
                        self.update_moderated_chats(
                            chat_id=message.chat.id,
                            start_time=start_time,
                            end_time=end_time,
                            is_active=True
                        )
                        self.logger.info('Установлен режим тишины ({:02d}:{:02d}-{:02d}:{:02d}) в чате {}, пользователь {} ({}).'.format(
                            *start_time, *end_time, message.chat.id, message.from_user.id, message.from_user.username
                        ))

                        sent = self.bot.send_message(
                            message.chat.id,
                            'Ежедневный режим тишины в чате установлен. '
                                + 'Все сообщения, отправленные с {:02d}:{:02d} до {:02d}:{:02d} мск, будут удаляться автоматически.\n'.format(
                                    *start_time, *end_time)
                                + 'Для изменения временных рамок используйте команду повторно с другими параметрами.\n'
                                + 'Для отключения режима тишины воспользуйтесь командой /moder_off.\n',
                                timeout=self.TIMEOUT
                        )
                        self.logger.info('Отправлено сообщение в группу {}: "{}".'.format(
                            sent.chat.id,
                            prepare_text_for_logging(sent.text)
                        ))
                else:
                    # если команду ввёл не администратор, сообщение удаляется
                    self.bot.delete_message(message.chat.id, message.id)
                    self.logger.info('Группа {} - удалено сообщение "{}" от пользователя {} ({}).'.format(
                        message.chat.id,
                        prepare_text_for_logging(message.text),
                        message.from_user.id,
                        message.from_user.username
                    ))
            else:
                # в приватном чате команда обрабатывается как обычный текст
                handle_message(message)


        @self.bot.message_handler(commands=['moder_off'])
        def moder_off(message):
            """Отключает режим тишины в чате."""

            if message.chat.type != 'private':
                self.logger.info('Группа {} - отправлена команда "{}" пользователем {} ({}) ({})'.format(
                    message.chat.id,
                    prepare_text_for_logging(message.text),
                    message.from_user.id,
                    message.from_user.username,
                    'админ или создатель чата' if self.is_by_admin(message) else 'не адмим'
                ))

                if self.is_by_admin(message):
                    if message.chat.id in self.moderated_chats:
                        self.update_moderated_chats(chat_id=message.chat.id, is_active=False)
                        self.logger.info('Режим тишины отключён в чате {} пользователем {} ({})'.format(
                            message.chat.id, message.from_user.id, message.from_user.username
                        ))

                        sent = self.bot.send_message(
                            message.chat.id,
                            'Режим тишины отключён. Чтобы вновь его активировать, введите команду:\n/moder_on время_начала время_окончания (время московское, формат - чч:мм).',
                            parse_mode='HTML',
                            timeout=self.TIMEOUT
                        )
                        self.logger.info('Отправлено сообщение в группу {}: "{}".'.format(
                            sent.chat.id,
                            prepare_text_for_logging(sent.text)
                        ))
                    else:
                        sent = self.bot.send_message(
                            message.chat.id,
                            'Режим тишины ещё не активирован в этом чате. Для его активации введите команду:\n/moder_on время_начала время_окончания (время московское, формат - чч:мм).',
                            parse_mode='HTML',
                            timeout=self.TIMEOUT
                        )
                        self.logger.info('Отправлено сообщение в группу {}: "{}".'.format(
                            sent.chat.id,
                            prepare_text_for_logging(sent.text)
                        ))
                else:
                    # если команду ввёл не администратор, сообщение удаляется
                    self.bot.delete_message(message.chat.id, message.id)
                    self.logger.info('Группа {} - удалено сообщение "{}" от пользователя {} ({}).'.format(
                        message.chat.id,
                        prepare_text_for_logging(message.text),
                        message.from_user.id,
                        message.from_user.username
                    ))
            else:
                # в приватном чате команда обрабатывается как обычный текст
                handle_message(message)
        

        @self.bot.message_handler(content_types=[
            'audio', 'photo', 'voice', 'video', 'document',
            'text', 'location', 'contact', 'sticker'
        ])
        def handle_message(message):
            """Обрабатывает сообщения от пользователя (любые)."""

            if message.chat.type == 'private':
                self.logger.info('Личный чат - сообщение от пользователя {} ({}): {}.'.format(
                    message.from_user.id, message.from_user.username,
                    '"{}"'.format(prepare_text_for_logging(message.text))
                        if message.content_type == 'text'
                        else '<{}>'.format(message.content_type)
                ))
                if message.from_user.id in self.user_table:
                    post, _ = self.user_table[message.from_user.id]

                    while True:
                        # получаем новые сообщения для отправки
                        post = post.get_next(message.text)
                        if post is None:
                            # сообщения кончились либо ожидается ответ от пользователя
                            break
                        self.send(received=message, new_post=post)
                        message.text = None
                else:
                    # пользователь ещё не нажал на "Старт"
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                    start_button = types.KeyboardButton(text='/start')
                    markup.add(start_button)

                    sent = self.bot.send_message(
                        message.from_user.id,
                        'Пожалуйста, перезапустите бота, введя команду /start.',
                        reply_markup=markup,
                        timeout=self.TIMEOUT
                    )
                    self.logger.info('Отправлено сообщение {}: {}.'.format(
                        'пользователю {} ({})'.format(
                            message.from_user.id, message.from_user.username
                        ) if message.chat.type == 'private'
                            else 'в группу {}'.format(message.chat.id),
                        '"{}"'.format(prepare_text_for_logging(sent.text))
                            if sent.content_type == 'text' else '<{}>'.format(sent.content_type)
                    ))
            else:
                # удаление сообщений, отправленных во время режима тишины
                if message.chat.id in self.moderated_chats:
                    (start_hour, start_minute), (end_hour,end_minute), is_active = self.moderated_chats[message.chat.id]
                    if is_active:
                        # проверяем, отправлено ли сообщение во время режима тишины
                        dt = datetime.fromtimestamp(message.date, config.TZ).timetuple()
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
                            self.logger.info('Группа {}, режим тишины - удалено сообщение {} от пользователя {} ({}).'.format(
                                message.chat.id,
                                '"{}"'.format(prepare_text_for_logging(message.text))
                                    if message.content_type == 'text' else '<{}>'.format(message.content_type),
                                message.from_user.id,
                                message.from_user.username
                            ))
    

    def _schedule_loop(self):
        # каждую минуту процедура ищет чаты, в которых в эту минуту по расписанию
        # начинается режим тишины, и отправляет сообщение о начале режима тишины
        # в эти чаты

        try:
            while self.is_alive:
                # вычисляем время до начала очередной минуты, и засыпаем на это время
                sec_delta = 60 - datetime.now(config.TZ).second

                for i in range(sec_delta):
                    if not self.is_alive:
                        return
                    time.sleep(1)

                hour = datetime.now(config.TZ).hour
                minute = datetime.now(config.TZ).minute

                for chat_id in self.moderated_chats:
                    (start_hour, start_minute), (end_hour,end_minute), is_active = self.moderated_chats[chat_id]
                    if is_active:
                        if hour == start_hour and minute == start_minute:
                            sent = self.bot.send_message(
                                chat_id,
                                text="🤫 Режим тишины в чате. Сообщения в период с {:02d}:{:02d} до {:02d}:{:02d} мск будут автоматически удаляться.".format(
                                    start_hour, start_minute, end_hour, end_minute
                                ),
                                timeout=self.TIMEOUT
                            )
                            self.logger.info('Группа {} - начался режим тишины ({:02d}:{:02d}-{:02d}:{:02d})'.format(
                                sent.chat.id, start_hour, start_minute, end_hour, end_minute
                            ))
                            self.logger.info('Отправлено сообщение в группу {}: "{}".'.format(
                                sent.chat.id,
                                prepare_text_for_logging(sent.text)
                            ))
        except Exception as e:
            self.logger.error(e)
        except KeyboardInterrupt as e:
            self.logger.info(e)
            self.stop()
    

    def start(self):
        """Запускает бота в текущем потоке."""

        self.is_alive = True
        
        # запускаем цикл расписания в отдельном потоке
        self._schedule_thread = Thread(target=self._schedule_loop)
        self._schedule_thread.start()

        # начинаем слушать бота
        telebot.apihelper.RETRY_ON_ERROR = True
        try:
            self.bot.infinity_polling(timeout=self.TIMEOUT)
        except Exception as e:
            self.logger.error('В infinity_polling() выпало исключение: {}.'.format(e))
        except KeyboardInterrupt as e:
            self.logger.info(e)
        finally:
            self.stop()


    def stop(self):
        """Останавливает бота."""
        try:
            self.logger.info('Запрос на остановку бота.')

            # останавливаем polling
            self.bot.stop_bot()

            # останавливаем поток с расписанием
            self.is_alive = False
            self._schedule_thread.join()

            self.logger.info('Бот остановлен.')
        except:
            self.stop()
    

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
            # markup_inline = types.InlineKeyboardMarkup()
            # for button in new_post.content:
            #     new_item = types.InlineKeyboardButton(text=button.text,
            #                                           callback_data=button.callback_data)
            #     markup_inline.add(new_item)
            # sent = self.bot.send_message(received.chat.id, new_post.caption,
            #                                reply_markup=markup_inline, timeout=self.TIMEOUT,
            #                                parse_mode='HTML')

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            for button in new_post.content:
                new_item = types.KeyboardButton(text=button.text)
                markup.add(new_item)
            sent = self.bot.send_message(received.chat.id, new_post.caption,
                                        reply_markup=markup, timeout=self.TIMEOUT,
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
            self.logger.error('Неизвестный тип сообщения, чат {}.'.format(received.chat.id))
        
        self.logger.info('Отправлено сообщение {}: {}.'.format(
            'пользователю {} ({})'.format(
                received.from_user.id, received.from_user.username
            ) if received.chat.type == 'private'
                else 'в группу {}'.format(received.chat.id),
            '"{}"'.format(prepare_text_for_logging(sent.text))
                if sent.content_type == 'text' else '<{}>'.format(sent.content_type)
        ))

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
