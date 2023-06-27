import wx  # pip install -U --pre -f https://wxpython.org/Phoenix/snapshot-builds/ wxPython
import wx.stc
import codecs
import code_analyzer


class Editor(wx.stc.StyledTextCtrl):
    """Класс текстового поля редактора."""
    def __init__ (self, parent, id = wx.ID_ANY, \
            pos = wx.DefaultPosition, \
            size = wx.DefaultSize,\
            style = 0,\
            name = 'editor',
            frame = None):
        wx.stc.StyledTextCtrl.__init__ (self, parent, id, pos, size, style, name)

        self.frame = frame

        # задаём боковую панель с номерами строк
        # TODO: расширение панели
        self.SetMarginWidth(1, 40)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(2, 10)

        # создаем кодировщик один раз в конструкторе,
        # чтобы не создавать его при каждой необходимости
        self.encoder = codecs.getencoder('utf-8')

        # стиль по умолчанию
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, 'size:%d' % 12)

        # определение стилей подсветки
        self.style_def = 0
        self.style_gray = 1
        self.style_purple = 2
        self.style_blue = 3
        self.style_green = 4

        # стили для текста в поле ввода
        self.StyleSetSpec(self.style_def, "face:Consolas,size:12,fore:#000000")
        self.StyleSetSpec(self.style_gray, "face:Consolas,size:12,fore:#888888")
        self.StyleSetSpec(self.style_purple, "face:Consolas,size:12,fore:#C800C8,bold")
        self.StyleSetSpec(self.style_blue, "face:Consolas,size:12,fore:#000096,bold")
        self.StyleSetSpec(self.style_green, "face:Consolas,size:12,fore:#009600,italic")

        self.code_analyzer = code_analyzer.CodeAnalyzer()

        # подписка на событие, когда нужно изменить стиль
        self.Bind(wx.stc.EVT_STC_STYLENEEDED, self.onStyleNeed)

        self.analyzed = None  # список кортежей с результатом анализа текста

        # подписка на событие "Добавление символа"
        self.Bind(wx.stc.EVT_STC_CHARADDED, self.onCharAdded)

        # заменяем табы на пробелы
        self.SetIndent(self.code_analyzer.INDENT_SPACE_COUNT)
        self.SetUseTabs(False)


    def onCharAdded(self, event):
        # # получим код нажатой клавиши
        # key_val = event.GetKey()

        #  # нас не интересуют нажатые клавиши с кодом больше 127
        # if key_val>127:
        #     return

        # # получим символ нажатой клавиши
        # key = chr(key_val)

        # if key == self.code_analyzer.QUOTE:
        #     pos = self.GetCurrentPos()
        #     # дописываем закрывающуюся кавычку
        #     self.AddText(self.code_analyzer.QUOTE)
        #     # установим каретку перед закрывающейся кавычкой
        #     self.GotoPos(pos)
        # получим код нажатой клавиши
        key_val = event.GetKey()


    def onPosChange (self, event):
        # Получим текущую позицию каретки в байтах
        pos = self.GetCurrentPos()
        text_left = self.GetTextRange(0, pos)
        self.GetParent().GetParent().GetParent().SetTitle(str (len (text_left) ) )


    def calcByteLen(self, text):
        """Посчитать длину строки в байтах, а не в символах"""
        return len(self.encoder(text)[0])


    def calcBytePos(self, text, pos):
        """Преобразовать позицию в символах в позицию в байтах"""
        return len(self.encoder(text[:pos])[0])


    def onStyleNeed(self, event):
        """Подсветка синтаксиса."""
        text = self.GetText()

        # cначала ко всему тексту применим стиль по умолчанию
        self.StartStyling(0)
        self.SetStyling(self.calcByteLen(text), self.style_def)

        analyzed, completion = self.code_analyzer.get_words(text)

        if completion:
            self.AddText(completion)
        # self.SetCurrentPos(len(completed_code))

        scene_idxs = []
        for i, (word, line_number, last_pos, word_type) in enumerate(analyzed):
            pos = last_pos-len(word)
            bytepos = self.calcBytePos(text, pos)  # находим начальную позицию в байтах
            text_byte_len = self.calcByteLen(word)  # вычисляем длину слова в байтах
            # применяем стиль
            self.StartStyling(bytepos)
            if word_type == self.code_analyzer.STRING:
                self.SetStyling(text_byte_len, self.style_green)
            elif word_type == self.code_analyzer.COMMENT:
                self.SetStyling(text_byte_len, self.style_gray)
            elif word_type == self.code_analyzer.KEYWORD:
                if word == self.code_analyzer.BOT or word == self.code_analyzer.BOT_END or\
                   word == self.code_analyzer.BLOCK or word == self.code_analyzer.BLOCK_END:
                    self.SetStyling(text_byte_len, self.style_purple)
                else:
                    self.SetStyling(text_byte_len, self.style_blue)

        self.analyzed = analyzed
