#/usr/bin/env python

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMenu, QCursor
from PyQt4.QtCore import QPoint, QString

from contextMenu import *

class DraggableNode(object):
    def __init__(self, parent, name, node_num = None):
        self.parent = parent
        self.frame = self.parent.parent
        self.name = name
        self.node_num = node_num
        self.press = None
        self.collection = None
        self.connect()

    def connect(self):
        self.cidpress = self.parent.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidmotion = self.parent.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidrelease = self.parent.fig.canvas.mpl_connect('button_release_event', self.on_release)

    def set_node_num(parent, self, node_num):
        self.node_num = node_num

    def on_press(self, event):
        collection = self.parent.get_artist(self.parent)
        for obj in collection.contains(event):
            
            if obj != True and obj != False: #obj is a dictionary
                if len(obj['ind']) > 0:
                    if str(obj['ind'][0]) == str(self.node_num):
                        print 'Twas me!:', self.name
                        if event.button == 3:
                            self.context_menu() #popup menu on right mouseclick
                        if event.button == 2:
                            self.press = event.xdata, event.ydata #save coords for node movement

    def on_motion(self, event):
        collection = self.parent.get_artist(self.parent)
        for obj in collection.contains(event):
            
            if obj != True and obj != False: #obj is a dictionary
                if len(obj['ind']) > 0: #at least one node activated
                    if str(obj['ind'][0]) == str(self.node_num): #found self in event list
                        self.parent.status_bar.showMessage('File Name: "'+str(self.name)+'"', 2500)
                        
        # If self.press is set, it means
        # 1) self.press gets set in on_press()
        # 2) self.press can only be set in one instance of DraggableNode at a time
        # 3) therefore, only the instance with self.press set will move
        # downside: kinda slow
        if self.press != None:
            xpress,ypress = self.press
            self.parent.pos[self.name][0] = event.xdata
            self.parent.pos[self.name][1] = event.ydata
            self.parent.redraw(self.parent)
                    
    def on_release(self, event):
        self.press = None
        self.parent.redraw(self.parent)

    def context_menu(self):
        cm = ContextMenu(self.name, self)
        cm.popup(QCursor.pos())

    def disconnect(self, node):
        node.parent.fig.canvas.mpl_disconnect(node.cidpress)
        node.parent.fig.canvas.mpl_disconnect(node.cidmotion)
        node.parent.fig.canvas.mpl_disconnect(node.cidrelease)
        
