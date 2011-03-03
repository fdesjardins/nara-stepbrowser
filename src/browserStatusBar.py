#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QStatusBar, QLabel, QPalette

class BrowserStatusBar(QtGui.QStatusBar):
    def __init__(self, parent = None):
        self.parent = parent

        QtGui.QStatusBar.__init__(self)
        
        self.status_text = QLabel(self.parent.step_path)
        self.addWidget(self.status_text, 1)

        style = 'QWidget { background-color: rgb(245,245,245); }'
        self.setStyleSheet(style)
