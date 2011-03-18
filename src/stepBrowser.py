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
        self.matplot_frame = BrowserMatPlotFrame(self)
        self.menu_bar = BrowserMenuBar(self)
        
        #Create Layout
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.menu_bar)
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
The STEP file browser allows you to visualize the hierarchical 
structure of mechanical assemblies represented using STEP files. 

Select a representation in the drop-down box in the bottom-left 
corner, and press the draw button. 

Now, you can move nodes using the left mouse button, and open a 
context menu using the right mouse button. 

Transformations may be applied using the matplotlib navigation toolbar 
below the plotting area.
'''
        QMessageBox.about(self, "Manual for Step File Browser", msg.strip())

    def open_file(self, f):
        os.system('gedit ' + self.step_path + '/' + f)

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

    def set_directory(self):
        filedialog = QtGui.QFileDialog()
        tmp = filedialog.getExistingDirectory(None, 'Open Directory', '')
        self.set_step_path(str(tmp))
        os.chdir(self.step_path)

    def set_step_path(self, path):
        self.step_path = path
        self.matplot_frame.step_path = path
        self.status_bar.showMessage("STEP directory changed to %s" % path, 2500)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
