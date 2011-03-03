#!/usr/bin/env python

"""
Step File Browser, Top Level

Ported to Qt by: Forrest Desjardins
"""

import sys, os, random

from PyQt4.QtCore import *
from PyQt4.QtGui import *

## user defined
from browserAddressBar import *
from browserMenuBar import *
from browserMatPlotFrame import *
from browserStatusBar import *


class StepBrowser(QtGui.QWidget):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Step File Browser')

        self.step_path = None

        #Create Widgets
        self.status_bar = BrowserStatusBar(self)
        self.address_bar = BrowserAddressBar(self)
        self.matplot_frame = BrowserMatPlotFrame(self)
        self.menu_bar = BrowserMenuBar(self)
        
        #Create Layout
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.menu_bar)
        vbox.addWidget(self.address_bar)
        vbox.addWidget(self.matplot_frame)
        vbox.addWidget(self.status_bar)
        self.setLayout(vbox)

        
    def about(self):
        msg = '''
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex 
ea commodo consequat. Duis aute irure dolor in reprehenderit in 
voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur 
sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
mollit anim id est laborum.
'''
        QMessageBox.about(self, "About the Step File Browser", msg.strip())


    def manual(self):
        msg = '''
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex 
ea commodo consequat. Duis aute irure dolor in reprehenderit in 
voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur 
sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
mollit anim id est laborum.
'''
        QMessageBox.about(self, "Manual for Step File Browser", msg.strip())


    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        canvas = self.matplot_frame.canvas
        mydpi = self.matplot_frame.dpi

        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            canvas.print_figure(path, dpi=mydpi) #save file
            self.status_bar.showMessage('Saved to %s' % path, 2500)


    def set_step_path(self, path):
        self.step_path = path
        self.address_bar.set_address(path)
        self.status_bar.showMessage("STEP directory changed to %s" % path, 2500)

        
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
