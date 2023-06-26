import wx
import wx.html


class HelpDialog(wx.Dialog):
    def __init__(self, parent, path_to_html):
        super().__init__(parent, title="Руководство пользователя", style=wx.DEFAULT_FRAME_STYLE)

        self.parent = parent

        self.html = wx.html.HtmlWindow(self, wx.ID_ANY)

        with open(path_to_html, 'tr', encoding='utf-8') as f:
            self.markup = f.read()

        self.html.SetPage(self.markup)

        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.Destroy()
        self.parent.help_dlg = None


class DocDialog(wx.Dialog):
    def __init__(self, parent, path_to_html):
        super().__init__(parent, title="Спецификация языка", style=wx.DEFAULT_FRAME_STYLE)

        self.html = wx.html.HtmlWindow(self, wx.ID_ANY)

        self.parent = parent

        with open(path_to_html, 'tr', encoding='utf-8') as f:
            self.markup = f.read()

        self.html.SetPage(self.markup)

        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.Destroy()
        self.parent.doc_dlg = None
