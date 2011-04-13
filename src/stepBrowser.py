#!/usr/bin/env python

"""
Step File Browser, Top Level

Ported to Qt and further developed by: Forrest Desjardins
"""

import os, sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QMessageBox, QFileDialog

## user defined
from browserMenuBar import BrowserMenuBar
from browserMatPlotFrame import BrowserMatPlotFrame
from browserStatusBar import BrowserStatusBar
from clusteringConfig import ClusteringConfig
from consoleDialog import ConsoleDialog

class StepBrowser(QtGui.QWidget):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, None)
        self.parent = parent
        self.setWindowTitle('STEP File Browser')
        
        self.step_path = None

        # Create Widgets
        self.status_bar = BrowserStatusBar(self)
        self.matplot_frame = BrowserMatPlotFrame(self)
        self.matplot_frame.on_draw()
        self.menu_bar = BrowserMenuBar(self)

        # Redirect stdout,stderr to dialog window
        self.console_dialog = ConsoleDialog(sys.stdout)
        sys.stdout = self.console_dialog
        sys.stderr = self.console_dialog

        # Clustering Config Window
        self.clust_config = ClusteringConfig(self)
        
        # Create Layout
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.menu_bar)
        vbox.addWidget(self.matplot_frame)
        vbox.addWidget(self.status_bar)
        self.setLayout(vbox)

        self.resize(800,700)

    def about(self):
        msg = '''
The STEP file browser allows the visualization of the hierarchical 
structure of mechanical assemblies represented in STEP files.

This program is intended to be useful in providing high-level overview
of complex topologies contained in these hierarchical assemblies.

The STEP file browser is a joint project between West Virginia University,
the US Navy, and the National Archives and Records Administration.

Contributors:

Desjardins, Forrest
Keczan, Jeremy
McGraw, Tim
'''
        QMessageBox.about(self, "About the STEP File Browser", msg.strip())

    def manual(self):
        msg = '''
Select a representation in the drop-down box in the bottom-left 
corner, and press the draw button. 

Move nodes using the middle mouse button, and open a 
context menu using the right mouse button. Left-click selects
a node, while Ctrl+Left-click adds a node to the current selection.

Transformations may be applied using the navigation toolbar 
above the plotting area.
'''
        QMessageBox.about(self, "Manual for Step File Browser", msg.strip())
        
    def cluster_config(self):
        self.clust_config._show()

    def console(self):
        self.console_dialog.show()

    def open_file(self, f):
        os.system('gedit ' + self.step_path + '/' + str(f))

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
        print "STEP directory changed to %s" % path

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
