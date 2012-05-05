#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import webbrowser

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

import const
from minix import QWidgetMinix

class Dictview(QFrame, QWidgetMinix):

    URL = 'http://dict-client.iciba.com/index.php?c=client&word=%s&dictlist=%s'
    DICTLIST = [1,101,3,2,102,4,5,103]
    WIDTH = 700
    HEIGHT = 540
    ALLOW_LENGTH = 25

    detailLinkClicked = Signal(str)

    def __init__(self):
        super(Dictview, self).__init__()
        self.init_window()
        self.init_webview()
        self.init_toolbar()
        self.init_layout()
        self.init_screen_info()
        self.init_config()

    def init_window(self):
        self.setWindowTitle('StrengthWord')
        self.resize(Dictview.WIDTH, Dictview.HEIGHT)
        self.screen_center()

    def init_webview(self):
        self.webview = QWebView(self)
        self.webpage = self.webview.page()
        self.webframe = self.webpage.mainFrame()

        self.webpage.setViewportSize(QSize(Dictview.WIDTH, Dictview.HEIGHT))
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

    def init_screen_info(self):
        rect = QDesktopWidget().availableGeometry()
        self.screen_width = rect.width()
        self.screen_height = rect.height()

    def init_config(self):
        self.dictlist = Dictview.DICTLIST
        self.window_width = Dictview.WIDTH
        self.window_height = Dictview.HEIGHT
        self.allow_length = Dictview.ALLOW_LENGTH

    def on_query_lineedit_returnPressed(self):
        text = self.query_lineedit.text()
        self.query(text)

    def on_webview_loadFinished(self):
        if self.webview.url().toString() == 'about:blank':
            return

        word = self.webview.url().queryItemValue('word')
        self.query_lineedit.setText(word)
        if self.webview.title() == u'爱词霸在线词典':
            self.run_javascript()
        else:
            html = const.not_fount_html % {'word': word}
            self.webview.blockSignals(True)
            self.webview.setHtml(html)
            self.webview.blockSignals(False)

        self.show()

    def on_webview_linkClicked(self, url):
        if url.fragment() == 'detail':
            self.hide()
            word = url.queryItemValue('word')
            self.detailLinkClicked.emit(word)
            return

        if url.host() != 'dict-client.iciba.com':
            self.hide()
            webbrowser.open(url.toString())
            return

        self.webview.load(url)

    def enable_debug(self, value=True):
        self.webview.settings().setAttribute(
            QWebSettings.WebAttribute.DeveloperExtrasEnabled, value)

    def setWindowFlags(self, flags):
        if flags == Qt.Popup:
            self.setStyleSheet('QFrame {border: 1px solid #55AAFF;}')
            self.toolbar.hide()
        else:
            self.setStyleSheet('')
            self.toolbar.show()

        QFrame.setWindowFlags(self, flags)

    def show(self):
        if self.windowType() == Qt.Popup:
            self.fix_page_content_size()
            if not self.isActiveWindow():
                self.follow_mouse()
            self.inside_screen()
        else:
            self.setStyleSheet('')

        QFrame.show(self)
        self.activateWindow()

        if self.query_lineedit.isVisible():
            self.query_lineedit.setFocus()

    def run_javascript(self):
        # 执行一些修复性 Javascript
        word = self.webview.url().queryItemValue('word')
        if self.windowType() == Qt.Popup:
            window_type_js = const.popup_js % {'word': word}
        else:
            window_type_js = const.window_js % {'word': word}

        self.webframe.addToJavaScriptWindowObject('python', QObject())
        self.webframe.evaluateJavaScript(const.common_js)
        self.webframe.evaluateJavaScript(window_type_js)

    def fix_page_content_size(self):
        # 用 Javascript 获得页面有效高度
        get_new_height = lambda: int(self.webframe.evaluateJavaScript(
            'document.documentElement.scrollHeight')) + 2 # 2 是边框

        # 把当前窗口设置为页面高度
        height1 = get_new_height()
        self.resize(self.size().width(), height1)

        # 有时候会出现滚动条，再检查一次
        height2 = get_new_height()
        if height1 != height2:
            self.resize(self.size().width(), height2)

    def create_url(self, text):
        url = Dictview.URL % (text, ','.join(map(str, self.dictlist)))
        return QUrl(url)

    def query(self, text):
        text = text.strip()
        if text == '':
            return

        exceed_count = len(text) - self.allow_length

        # 选中大量文本，不取词
        if exceed_count > 0:
            html = const.too_long_html % {'exceed_count': exceed_count}
            self.webview.blockSignals(True)
            self.webview.setHtml(html)
            self.webview.blockSignals(False)
            self.show()
            return

        url = self.create_url(text)
        self.webview.load(url)

def test_window():
    app = QApplication(sys.argv)
    dictview = Dictview()
    dictview.enable_debug()
    dictview.query('test')
    dictview.show()
    app.exec_()

def test_popup():
    app = QApplication(sys.argv)
    dictview = Dictview()
    dictview.setWindowFlags(Qt.Popup)
    dictview.dictlist = [1, 101]
    dictview.resize(360, 360)
    dictview.query('test')
    exit_button = QPushButton('Exit')
    exit_button.clicked.connect(QApplication.quit)
    exit_button.show()
    app.exec_()

def main():
    test_window()
    #test_popup()

if __name__ == '__main__':
    main()
