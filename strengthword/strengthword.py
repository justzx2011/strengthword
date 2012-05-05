#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

from dictview import Dictview

class StrengthWord(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.init_dictviews()
        self.init_clipboard()
        self.init_tray()
        QApplication.setQuitOnLastWindowClosed(False)

    def init_dictviews(self):
        self.window_dictview = Dictview()
        self.popup_dictview = Dictview()
        self.popup_dictview.setWindowFlags(Qt.Popup)
        self.popup_dictview.dictlist = [1, 101]
        self.popup_dictview.resize(360, 360)
        self.popup_dictview.detailLinkClicked.connect(
            self.window_dictview.query)

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

    def show(self):
        self.trayicon.show()
        self.window_dictview.show()

    def on_show_action_triggered(self):
        if self.show_action.isChecked():
            self.window_dictview.show()
        else:
            self.window_dictview.hide()

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

        visible = self.window_dictview.isVisible()
        if visible:
            self.window_dictview.hide()
        else:
            self.window_dictview.show()
        self.show_action.setChecked(not visible)

    def on_clipboard_selectionChanged(self):
        text = self.clipboard.text(QClipboard.Selection)
        self.popup_dictview.query(text)

    def on_dictview_detailLinkClicked(self, word):
        print 'click mini deatil: ' + word

def main():
    app = QApplication(sys.argv)
    strengthword = StrengthWord()
    strengthword.show()
    app.exec_()

if __name__ == '__main__':
    main()
