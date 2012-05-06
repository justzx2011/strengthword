#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide.QtCore import *
from PySide.QtGui import *

class QWidgetMinix(object):

    def screen_center(self):
        center_point = QDesktopWidget().availableGeometry().center()
        geometry = self.frameGeometry()
        geometry.moveCenter(center_point)
        self.move(geometry.topLeft())

    def follow_mouse(self):
        x, y = QCursor.pos().toTuple()

        # 比鼠标位置稍微右下一点
        x += 15
        y += 15

        self.move(QPoint(x, y))

    def inside_screen(self):
        x, y = self.pos().toTuple()
        width, height = self.size().toTuple()

        # 避免超出屏幕边缘
        rect = QDesktopWidget().availableGeometry()

        right_outside = x + width - rect.width()
        if right_outside > 0:
            x -= right_outside

        bottom_outside = y + height - rect.height()
        if bottom_outside > 0:
            y -= bottom_outside

        self.move(QPoint(x, y))

    def bind_signals(self):
        if not hasattr(self, 'singals'):
            return

        for widget_name, singal_name in self.singals():
            callback_name = 'on_%s_%s' % (widget_name, singal_name)
            callback_func = getattr(self, callback_name)
            widget = getattr(self, widget_name)
            widget_singlas = getattr(widget, singal_name)
            widget_singlas.connect(callback_func)

    def alert(self, message_type, message_text):
        dialog = QMessageBox()
        dialog.setIcon(message_type)
        dialog.setText("%s" % message_text)
        dialog.exec_()
