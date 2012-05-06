#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

from minix import QWidgetMinix
from dictview import WordView, PopupWordView, SentenceView

class StrengthWord(QWidget, QWidgetMinix):

    WIDTH = 700
    HEIGHT = 540

    def __init__(self):
        QWidget.__init__(self)
        self.init_window()
        self.init_dictviews()
        self.init_tabwidget()
        self.init_clipboard()
        self.init_tray()
        self.init_layout()
        QApplication.setQuitOnLastWindowClosed(False)

    def init_window(self):
        self.setWindowTitle('StrengthWord')
        self.resize(StrengthWord.WIDTH, StrengthWord.HEIGHT)
        self.screen_center()

    def init_dictviews(self):
        self.wordview = WordView()
        self.popup_wordview = PopupWordView()
        self.popup_wordview.detailLinkClicked.connect(
            self.wordview.query)
        self.sentenceview = SentenceView()
        self.sentenceview.enable_debug()

    def init_tabwidget(self):
        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.wordview, u'词典')
        self.tabwidget.addTab(self.sentenceview, u'句库')

        self.tabwidget.currentChanged.connect(self.on_tabwidget_currentChanged)

    def init_clipboard(self):
        self.clipboard = QApplication.clipboard()
        self.clipboard.selectionChanged.connect(
            self.on_clipboard_selectionChanged)

    def init_tray(self):
        self.show_action = QAction(
            u"显示", self, triggered=self.on_show_action_triggered)
        self.show_action.setCheckable(True)
        self.show_action.setChecked(True)

        self.scan_action = QAction(
            u"取词", self, triggered=self.on_scan_action_triggered)
        self.scan_action.setCheckable(True)
        self.scan_action.setChecked(True)

        self.quit_action = QAction(u"退出", self, triggered=QApplication.quit)

        self.trayicon_menu = QMenu(self)
        self.trayicon_menu.addAction(self.show_action)
        self.trayicon_menu.addAction(self.scan_action)
        self.trayicon_menu.addAction(self.quit_action)

        self.trayicon = QSystemTrayIcon(
            QIcon.fromTheme('gnome-dictionary'), self)
        self.trayicon.setContextMenu(self.trayicon_menu)
        self.trayicon.activated.connect(self.on_trayicon_activated)

    def init_layout(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.tabwidget)
        self.setLayout(self.layout)

    def show(self):
        self.trayicon.show()
        QWidget.show(self)
        self.wordview.query_lineedit.setFocus()

    def on_show_action_triggered(self):
        self.setVisible(self.show_action.isChecked())

    def on_scan_action_triggered(self):
        if self.scan_action.isChecked():
            self.clipboard.selectionChanged.connect(
                self.on_clipboard_selectionChanged)
        else:
            self.clipboard.selectionChanged.disconnect(
                self.on_clipboard_selectionChanged)

    def on_trayicon_activated(self, reason):
        if reason != QSystemTrayIcon.Trigger:
            return

        visible = self.isVisible()
        self.setVisible(not visible)
        self.show_action.setChecked(not visible)

    def on_clipboard_selectionChanged(self):
        text = self.clipboard.text(QClipboard.Selection)
        self.popup_wordview.query(text)

    def on_tabwidget_currentChanged(self, index):
        if index == 0: # self.wordview
            self.wordview.query(self.sentenceview.current_word())
            self.wordview.query_lineedit.setFocus()
        elif index == 1: # self.sentenceview
            self.sentenceview.query(self.wordview.current_word())
            self.sentenceview.query_lineedit.setFocus()

    def showEvent(self, event):
        self.show_action.setChecked(True)

    def closeEvent(self, event):
        self.show_action.setChecked(False)

def main():
    app = QApplication(sys.argv)
    strengthword = StrengthWord()
    strengthword.show()
    app.exec_()

if __name__ == '__main__':
    main()
