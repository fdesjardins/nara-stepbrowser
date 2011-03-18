#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox, QFileDialog

class BrowserMenuBar(QtGui.QMenuBar):
    def __init__(self, parent = None):
        QtGui.QMenuBar.__init__(self)
        self.parent = parent

        #File Menu
        file_menu = self.addMenu("&File")
        open_action = self.create_action("&Open...", "Ctrl+D", "Open a directory containing STEP files", slot = parent.set_directory)
        save_file_action = self.create_action("&Save Plot", "Ctrl+S", "Save plot as image file", slot = parent.save_plot)
        quit_file_action = self.create_action("&Quit", "Ctrl+Q", "Close the STEP file browser", slot = parent.close)
        file_menu.addAction(open_action)
        file_menu.addAction(save_file_action)
        file_menu.addAction(quit_file_action)

        #View Menu
        view_menu = self.addMenu("&View")
        fullscreen_action = self.create_action("&Full Screen", "Ctrl+F", "Show the browser in full screen mode",
                                                    slot = parent.toggle_fullscreen, checkable = True)
        grid_view_action = self.create_action("&Grid", "Ctrl+G", "Show gridlines on the current plot", 
                                                   slot = parent.matplot_frame.draw_grid, checkable = True)
        axis_units_view_action = self.create_action("&Axis Units", "Ctrl+A", "Show axis units on the current plot",
                                                         slot = parent.matplot_frame.toggle_axis_units, checkable = True)
        node_labels_view_action = self.create_action("Node &Labels", "Ctrl+L", "Show node labels on the current plot",
                                                         slot = parent.matplot_frame.toggle_node_labels, checkable = True)
        view_menu.addAction(fullscreen_action)
        view_menu.addAction(grid_view_action)
        view_menu.addAction(axis_units_view_action)
        view_menu.addAction(node_labels_view_action)
        
        #Dialogs Menu
        #dialogs_menu = self.addMenu("&Dialogs")
        #manual_help_action = self.create_action("", "F3", "", slot = parent.manual)
        #dialogs_menu.addAction(manual_help_action)

        #Help Menu
        help_menu = self.addMenu("&Help")
        manual_help_action = self.create_action("&Manual", "F3", "Open the program documentation", slot = parent.manual)
        about_help_action = self.create_action("&About", "F1", "About the file browser", slot = parent.about)
        help_menu.addAction(manual_help_action)
        help_menu.addAction(about_help_action)
       

    def create_action(self, text, shortcut = None, tip = None, slot = None, 
                      checkable = False, duration = 2500, icon = None):

        action = QtGui.QAction(text, self.parent)

        #Action attributes
        if icon is not None: 
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None: 
            action.setShortcut(shortcut)
        if tip is not None: 
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)

        #Action signal/slot connections
        self.connect(action, QtCore.SIGNAL('triggered()'), slot)
        self.connect(action, QtCore.SIGNAL('hovered()'), 
                     (lambda x=duration: self.parent.status_bar.showMessage(action.statusTip(), x)))

        return action


    
