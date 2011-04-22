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
        
        #Edit Menu
        edit_menu = self.addMenu("&Edit")
        select_all_action = self.create_action("Select &All", "Ctrl+A",
                                               "Select all items in this window",
                                               slot = (lambda x=0: parent.matplot_frame.g.select_all()))
        select_none_action = self.create_action("Select &None", "Ctrl+Shift+A",
                                                "Deselect all items in this window",
                                                slot = (lambda x=0: parent.matplot_frame.g.select_none()))
        select_matching_action = self.create_action("Select I&tems Matching...", "Ctrl+S",
                                                    "Select all items in this window matching a given pattern",
                                                    slot = (lambda x=0: parent.matplot_frame.g.select_matching()))
        select_inverse_action = self.create_action("In&vert Selection", "Ctrl+Shift+I",
                                                    "Select all and only the items in this window not currently selected (Can be slow)",
                                                    slot = (lambda x=0: parent.matplot_frame.g.select_inverse()))
        edit_menu.addAction(select_all_action)
        edit_menu.addAction(select_none_action)
        edit_menu.addAction(select_matching_action)
        edit_menu.addAction(select_inverse_action)

        #View Menu
        view_menu = self.addMenu("&View")
        fullscreen_action = self.create_action("&Full Screen", "Ctrl+F", "Show the browser in full screen mode",
                                                    slot = parent.toggle_fullscreen, checkable = True)
        grid_view_action = self.create_action("&Grid", "Ctrl+G", "Show gridlines on the current plot", 
                                                   slot = parent.matplot_frame.draw_grid, checkable = True)
        axis_units_view_action = self.create_action("&Axis Units", None, "Show axis units on the current plot",
                                                         slot = parent.matplot_frame.toggle_axis_units, checkable = True)
        node_labels_view_action = self.create_action("Node &Labels", "Ctrl+L", "Show node labels on the current plot",
                                                         slot = parent.matplot_frame.toggle_node_labels, checkable = True)
        clustering_config_view_action = self.create_action("Clustering Configuration", 
                                                           tip = "Change the way the clustering algorithm generates co-occurence and context graphs",
                                                           slot = parent.cluster_config, checkable = False)
        console_window_view_action = self.create_action("&Console Window", tip = "View messages and extra information about program activities",
                                                        slot = parent.console, checkable = False)
        graph_properties_view_action = self.create_action("Graph &Information", tip = "View general graphing properties and information",
                                                          slot = parent.matplot_frame.g.graph_info, checkable = False)
        
        view_menu.addAction(axis_units_view_action)
        view_menu.addAction(fullscreen_action)
        view_menu.addAction(grid_view_action)
        view_menu.addAction(node_labels_view_action); node_labels_view_action.setChecked(True);
        view_menu.addSeparator()
        view_menu.addAction(clustering_config_view_action)
        view_menu.addAction(console_window_view_action)
        view_menu.addAction(graph_properties_view_action)

        #Help Menu
        help_menu = self.addMenu("&Help")
        manual_help_action = self.create_action("&Manual", "F3", "Open the program documentation", slot = parent.manual)
        about_help_action = self.create_action("&About", "F1", "About the file browser", slot = parent.about)
        
        help_menu.addAction(about_help_action)
        help_menu.addAction(manual_help_action)

    def create_action(self, text, shortcut = None, tip = None, slot = None, 
                      checkable = False, duration = 3500, icon = None):

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
