#!/usr/bin/env python

import gc

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel, QSlider, QComboBox
from PyQt4.QtGui import QMessageBox, QSpinBox, QSpacerItem
from PyQt4.QtCore import Qt

import numpy
from numpy import arange, sin, pi

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

import networkx as NX

##user defined
from graphTest import GraphTest
from graphTestNumpy import GraphTestNumPy
from graphHierarchy import GraphHierarchy
from graphCoOccurrence import GraphCoOccurrence
from graphContext import GraphContext


class BrowserMatPlotFrame(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.status_bar = parent.status_bar

        #State
        self.draw_node_labels_tf = True
        self.draw_axis_units_tf = False
        self.draw_grid_tf = False
        self.g = None

        #PATH used in drawing STEP hierarchy, co-occurence, context
        self.step_path = parent.step_path
        
        #MPL figure
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
        
        #QT canvas
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('pick_event', self.on_pick) #used when selectingpyth	 canvas objects
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        
        self.axes = self.fig.add_subplot(111)
        #self.axes.hold(False) #clear the axes every time plot() is called

        self.mpl_toolbar = NavigationToolbar(self.canvas, self)

        #GUI controls
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Graph Test", 
                                  "Graph Test Numpy", 
                                  "STEP Hierarchy", 
                                  "STEP Co-occurence",
                                  "STEP Context"])
        self.mode_combo.setMinimumWidth(200)
        
        self.draw_button = QPushButton("&Draw/Refresh")
        self.connect(self.draw_button, QtCore.SIGNAL('clicked()'), self.on_draw)
        
        self.node_size = QSpinBox(self)
        self.node_size.setSingleStep(5)
        self.node_size.setMaximum(100)
        self.node_size.setValue(25)
        self.node_size_label = QLabel('Node Size (%):')
        # connection set in on_draw() method

        #Horizontal layout
        hbox = QtGui.QHBoxLayout()
    
        #Adding matplotlib widgets
        for w in [self.mode_combo, 's', self.node_size_label, self.node_size, self.draw_button]:
            if w == 's': hbox.addStretch()
            else:
                hbox.addWidget(w)
                hbox.setAlignment(w, Qt.AlignVCenter)

        #Vertical layout. Adding all other widgets, and hbox layout.
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.canvas.setFocus(True)
        
    def draw_axis_units(self):
        fw = self.fig.get_figwidth()
        fh = self.fig.get_figheight()

        l_margin = .4 / fw #.4in
        b_margin = .3 / fh #.3in

        if self.draw_axis_units_tf == True:
            self.fig.subplots_adjust(left=l_margin,right=1,top=1,bottom=b_margin)
        else: 
            self.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)

        self.canvas.draw()

    def draw_grid(self):
        if self.draw_grid_tf == False:
            self.draw_grid_tf = True
        else:
            self.draw_grid_tf = False
            
        self.axes.grid(self.draw_grid_tf)
        self.canvas.draw()

    def on_draw(self): 
        draw_mode = self.mode_combo.currentText()
        
        self.axes.clear()
        if self.g != None:
            if hasattr(self.g, 'destruct'):
                self.g.destruct()

        if draw_mode == "Graph Test":
            self.g = GraphTest(self)
        elif draw_mode == "Graph Test Numpy":
            self.g = GraphTestNumPy(self)
        elif draw_mode == "STEP Hierarchy":
            self.g = GraphHierarchy(self)
        elif draw_mode == "STEP Co-occurence":
            self.g = GraphCoOccurrence(self)
        elif draw_mode == "STEP Context":
            self.g = GraphCoOccurrence(self)

        self.connect(self.node_size, QtCore.SIGNAL('valueChanged(int)'), self.g.set_node_mult)
        self.axes.grid(self.draw_grid_tf)
        self.canvas.draw()
        
    def on_pick(self, args):
        print "in matplotframe: ", args

    def resizeEvent(self, ev):
        self.draw_axis_units()
        
    def set_step_path(self, path):
        self.step_path = path
        self.parent.set_step_path(path)

    def toggle_axis_units(self):
        if self.draw_axis_units_tf == False: 
            self.draw_axis_units_tf = True
        else:
            self.draw_axis_units_tf = False
        self.draw_axis_units()

    def toggle_node_labels(self):
        if self.draw_node_labels_tf == False: 
            self.draw_node_labels_tf = True
        else:
            self.draw_node_labels_tf = False

        if self.g != None:
            self.g.redraw()
