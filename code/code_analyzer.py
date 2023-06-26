import re

class CodeAnalyzer:
    # типы слов
    COMMENT = 0  # комментарий
    KEYWORD = 1  # ключевое слово
    STRING = 2  # строка в кавычках
    UNKNOWN = 3  # тип не определён

    # слова и символы, которые могут встречаться в тексте
    BOT = 'бот'
    BOT_END = 'конецБота'
    BLOCK = 'блок'
    BLOCK_END = 'конецБлока'
    TEXT = 'текст'
    PHOTO = 'фото'
    VOICE = 'гс'
    AUDIO = 'аудио'
    VIDEO = 'видео'
    GIF = 'гиф'
    DOC = 'документ'
    STICKER = 'стикер'
    GROUP = 'группа'
    GROUP_END = 'конецГруппы'
    WAIT_AUDIO = 'ждатьАудио'
    WAIT_TEXT = 'ждатьТекст'
    WAIT_END = 'хватитЖдать'
    BACK = 'назад'
    ELSE = 'иначе'
    EXIT = 'выход'
    BUTTONS = 'кнопки'
    BUTTONS_END = 'хватитКнопок'
    TRANSITION = 'переход'
    COLON = ':'
    DOUBLE_DASH = '->'
    EXCLAM = '!'
    QUOTE = '"'
    # CARRIAGE_RETURN = '\r'
    NEWLINE = '\r\n'
    SPACE = ' '

    # ключевые слова
    KWORDS = [BOT, BOT_END, BLOCK, BLOCK_END, TEXT, PHOTO, VOICE, AUDIO, VIDEO, GIF, DOC, STICKER,
              GROUP, GROUP_END, WAIT_AUDIO, WAIT_TEXT, WAIT_END, BACK, ELSE, EXIT, BUTTONS, BUTTONS_END,
              COLON, DOUBLE_DASH, TRANSITION]

    # показывает количество пробелов для каждого отступа
    INDENT_SPACE_COUNT = 4

    def __init__(self):
        pass

    # TODO: исправить выделение
    def autocomplete(self, code, analyzed, last_symbol, last_line_number):
        completion = ''
        # добавление отступа при переходе на новую строку
        if last_symbol == self.NEWLINE and last_line_number:
            # ищем последнюю введённую строку
            newline_start_idxs = [_.start() for _ in re.finditer(self.NEWLINE, code)]
            line_end = newline_start_idxs[-1]+len(self.NEWLINE)
            if len(newline_start_idxs)>1:
                line_start = newline_start_idxs[-2]+len(self.NEWLINE)
            else:
                line_start = 0
            last_line = code[line_start:line_end+1]
            # считаем количество пробелов в начале последней строки
            space_count = 0
            for symbol in last_line:
                if symbol == self.SPACE:
                    space_count += 1
                else:
                    break
            # добавляем на следующую строку такое же количество пробелов
            if space_count % self.INDENT_SPACE_COUNT == 0:
                completion += self.SPACE * space_count
            if analyzed:
                word, line_number, _, word_type = analyzed[-1]
                if word_type == self.KEYWORD and word == self.COLON and line_number == last_line_number-1:
                    # если пользователь ввёл двоеточие и нажал на Enter,
                    # отступ на следующей строке увеличивается
                    completion += self.SPACE * self.INDENT_SPACE_COUNT
        return completion


    def get_words_for_parsing(self, analyzed):
        """Принимает на вход список кортежей, сгенерированный функцией get_words, возвращает список
        кортежей для парсинга."""
        result = []  # список кортежей вида (слово, номер_строки, тип (строка или ключевое слово))
        for word, line_number, _, word_type in analyzed:
            if word_type == self.STRING:
                # убираем символы \r\n из строки и лишнее экранирования для табов и переводов строк
                word = word.replace(self.NEWLINE, '')\
                           .replace('\\t', '\t')\
                           .replace('\\n', '\n')
            if word_type != self.COMMENT:
                result.append((word, line_number, word_type))
        return result


    def get_words(self, code):
        analyzed = []  # список кортежей вида (слово, номер_строки, позиция_последнего_символа_в_тексте, тип)
        line_number = 1  # номер текущей строки
        current_word = ''  # текущее исследуемое слово
        current_type = self.UNKNOWN  # тип текущего исследуемого слова

        symbol = ''
        for i, symbol in enumerate(code):
            pos = i+1
            if symbol == '\r':
                symbol = self.NEWLINE
                pos += 1
            elif symbol == '\n':
                symbol = self.NEWLINE
                continue
            if symbol == self.QUOTE:
                if current_type == self.STRING:
                    # заканчиваем считывание строки в кавычках
                    analyzed.append((current_word+symbol,
                                   line_number-current_word.count(self.NEWLINE),
                                   pos, current_type))
                    current_word = ''
                    current_type = self.UNKNOWN
                    continue
                elif current_type != self.COMMENT:
                    # начинаем считывание строки в кавычках
                    current_word = ''
                    current_type = self.STRING
            elif symbol == self.NEWLINE:
                line_number += 1
                if current_type == self.COMMENT:
                    # комментарий прерывается при переходе на следующую строку
                    analyzed.append((current_word+symbol, line_number, pos, current_type))
                    current_word = ''
                    current_type = self.UNKNOWN
                    continue
            elif symbol == self.EXCLAM:
                if current_type != self.STRING and current_type != self.COMMENT:
                    # начинается комментарий
                    current_word = ''
                    current_type = self.COMMENT
            if current_type == self.KEYWORD and symbol != self.NEWLINE and\
               symbol != self.SPACE and symbol != self.COLON:
                # если после ввода ключевого слова пользователь ввёл что-то, кроме
                # пробела или перевода строки, ключевое слово теряется
                current_word, _, _, _ = analyzed[-1]
                del analyzed[-1]
            if current_type == self.KEYWORD:
                current_type = self.UNKNOWN
            if current_type == self.UNKNOWN and (symbol == self.NEWLINE or symbol == self.SPACE):
                current_word = ''
            else:
                current_word += symbol
            if current_word in self.KWORDS:
                current_type = self.KEYWORD
                analyzed.append((current_word, line_number, pos, current_type))
                current_word = ''
        if current_type == self.STRING or current_type == self.COMMENT:
            analyzed.append((current_word, line_number-current_word.count(self.NEWLINE), pos, current_type))

        completion = ''
        return analyzed, completion
