#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import webbrowser

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

import const
from minix import QWidgetMinix

class View(QFrame, QWidgetMinix):

    def __init__(self):
        QFrame.__init__(self)
        self.init_window()
        self.init_webview()
        self.init_toolbar()
        self.init_layout()

    def init_window(self):
        self.setWindowTitle('StrengthWord')
        self.screen_center()

    def init_webview(self):
        self.webview = QWebView(self)
        self.webpage = self.webview.page()
        self.webframe = self.webpage.mainFrame()

        self.webpage.setLinkDelegationPolicy(
            QWebPage.DelegateAllLinks);

        self.webview.loadFinished.connect(self.on_webview_loadFinished)
        self.webview.linkClicked.connect(self.on_webview_linkClicked)

        self.webview.blockSignals(True)
        self.webview.load(QUrl('about:blank'))
        self.webview.blockSignals(False)

    def init_toolbar(self):
        self.back_action = self.webview.pageAction(QWebPage.Back)
        self.forward_action = self.webview.pageAction(QWebPage.Forward)
        self.query_lineedit = QLineEdit()
        self.query_lineedit.returnPressed.connect(
            self.on_query_lineedit_returnPressed)
        self.query_toolbutton = QToolButton()
        self.query_toolbutton.setText(u'查一下')
        self.query_toolbutton.setIcon(QIcon.fromTheme('find'))
        self.query_toolbutton.clicked.connect(
            self.on_query_lineedit_returnPressed)

        self.toolbar = QToolBar(u'工具栏')
        self.toolbar.setMovable(False)
        self.toolbar.addAction(self.back_action)
        self.toolbar.addAction(self.forward_action)
        self.toolbar.addWidget(self.query_lineedit)
        self.toolbar.addWidget(self.query_toolbutton)

    def init_layout(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.webview)
        self.setLayout(self.layout)

    def on_query_lineedit_returnPressed(self):
        text = self.query_lineedit.text()
        self.query(text)

    def on_webview_loadFinished(self):
        raise NotImplementedError

    def on_webview_linkClicked(self, url):
        raise NotImplementedError

    def enable_debug(self, value=True):
        ''' 开启开发者工具 '''

        self.webview.settings().setAttribute(
            QWebSettings.WebAttribute.DeveloperExtrasEnabled, value)

    def current_word(self):
        return self.query_lineedit.text()

    def set_html(self, html):
        self.webview.blockSignals(True)
        self.webview.setHtml(html)
        self.webview.blockSignals(False)

    def show(self):
        QFrame.show(self)
        self.activateWindow()
        self.query_lineedit.setFocus()

    def create_url(self, text):
        raise NotImplementedError

    def query(self, text):
        text = text.strip()
        if text == '':
            return

        self.query_lineedit.setText(text)
        url = self.create_url(text)
        self.webview.load(url)

class WordView(View):

    def __init__(self):
        View.__init__(self)
        self.dictlist = [1,101,3,2,102,4,5,103]

    def on_webview_loadFinished(self):
        if self.webview.url().toString() == 'about:blank':
            return

        word = self.webview.url().queryItemValue('word')
        self.query_lineedit.setText(word)
        if self.webview.title() == u'爱词霸在线词典':
            js = self.get_run_javascript()
            self.webframe.evaluateJavaScript(js)
        else:
            html = const.wordview_not_found_html % {'word': word}
            self.set_html(html)

        self.show()

    def on_webview_linkClicked(self, url):
        if url.host() != 'dict-client.iciba.com':
            self.hide()
            webbrowser.open(url.toString())
            return

        self.webview.load(url)

    def get_run_javascript(self):
        word = self.webview.url().queryItemValue('word')
        js = const.wordview_common_js
        js += const.wordview_js % dict(word=word)
        return js

    def create_url(self, text):
        url_tpl = 'http://dict-client.iciba.com/index.php?c=client&word=%s&dictlist=%s'
        url = url_tpl % (text, ','.join(map(str, self.dictlist)))
        return QUrl(url)

class PopupWordView(WordView):

    detailLinkClicked = Signal(str)

    def __init__(self):
        WordView.__init__(self)
        self.dictlist = [1, 101]
        self.setWindowFlags(Qt.Popup)
        self.setStyleSheet('QFrame {border: 1px solid #55AAFF;}')
        self.resize(360, 360)
        self.webpage.setViewportSize(self.size())
        self.allow_length = 25
        self.toolbar.hide()

    def on_webview_linkClicked(self, url):
        if url.fragment() == 'detail':
            self.hide()
            word = url.queryItemValue('word')
            self.detailLinkClicked.emit(word)
            return

        WordView.on_webview_linkClicked(self, url)

    def get_run_javascript(self):
        word = self.webview.url().queryItemValue('word')
        js = const.wordview_common_js
        js += const.popup_wordview_js % dict(word=word)
        return js

    def auto_resize(self):
        ''' 用 Javascript 获得页面有效高度 '''

        get_new_height = lambda: int(self.webframe.evaluateJavaScript(
            'document.documentElement.scrollHeight')) + 2 # 2 是边框

        # 把当前窗口设置为页面高度
        height1 = get_new_height()
        self.resize(self.size().width(), height1)

        # 有时候会出现滚动条，再检查一次
        height2 = get_new_height()
        if height1 != height2:
            self.resize(self.size().width(), height2)

    def show(self):
        self.auto_resize()
        if not self.isActiveWindow():
            self.follow_mouse()
        self.inside_screen()
        WordView.show(self)

    def query(self, text):
        text = text.strip()
        if text == '':
            return

        exceed_count = len(text) - self.allow_length

        # 选中大量文本，不取词
        if exceed_count > 0:
            html = const.popup_wordview_too_long_html % \
                {'exceed_count': exceed_count}
            self.set_html(html)
            self.show()
            return

        self.query_lineedit.setText(text)
        url = self.create_url(text)
        self.webview.load(url)

class SentenceView(View):

    def __init__(self):
        View.__init__(self)

    def on_webview_loadFinished(self):
        if self.webview.url().toString() == 'about:blank':
            return

        word = self.webview.url().queryItemValue('s')
        self.query_lineedit.setText(word)
        if self.webview.title() == '2012 free interface':
            js = self.get_run_javascript()
            self.webframe.evaluateJavaScript(js)
        else:
            html = const.sentenceview_not_found_html % {'word': word}
            self.set_html(html)

        self.show()

    def get_run_javascript(self):
        return const.sentenceview_js

    def on_webview_linkClicked(self, url):
        pass

    def create_url(self, text):
        url = 'http://interface2010.client.iciba.com/?c=dj2012&s=%s' % text
        return QUrl(url)

def test_wordview():
    app = QApplication(sys.argv)
    wordview = WordView()
    wordview.enable_debug()
    wordview.query('test')
    wordview.show()
    app.exec_()

def test_popup_wordview():
    app = QApplication(sys.argv)
    dictview = PopupWordView()
    dictview.setWindowFlags(Qt.Popup)
    dictview.dictlist = [1, 101]
    dictview.resize(360, 360)
    dictview.query('test')
    exit_button = QPushButton('Exit')
    exit_button.clicked.connect(QApplication.quit)
    exit_button.show()
    app.exec_()

def test_sentenceview():
    app = QApplication(sys.argv)
    sentenceview = SentenceView()
    sentenceview.enable_debug()
    sentenceview.query('test')
    sentenceview.show()
    app.exec_()

def main():
    test_wordview()
    #test_popup_wordview()
    #test_sentenceview()

if __name__ == '__main__':
    main()
