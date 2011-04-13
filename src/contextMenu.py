from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMenu, QCursor
from PyQt4.QtCore import QString

class ContextMenu(QtGui.QMenu):
    def __init__(self, node_name, parent = None):

        node = parent
        self.graph = node.parent
        self.matplot_frame = self.graph.parent
        self.parent = self.matplot_frame.parent #stepbrowser

        QtGui.QMenu.__init__(self, self.matplot_frame)

        open_action = self.create_action("&Open File", tip = "Open " + str(node_name) + " using the default application.", 
                                         slot = (lambda x=node_name: self.parent.open_file(x)))
        
        center_on_node = self.create_action("Center on &Node",
                                            tip = "Transforms the canvas to fit the selected node and its neighors",
                                            slot = (lambda x=node_name: self.parent.open_file(x)))
        
        center_on_graph = self.create_action("Center on &Graph",
                                            tip = "Transforms the canvas to fit the selected node's containing graph",
                                            slot = (lambda x=node_name: self.parent.open_file(x)))
        
        self.addAction(open_action)
        self.addSeparator()
        self.addAction(center_on_node)
        self.addAction(center_on_graph)
        self.sizeHint()


    def create_action(self, text, shortcut = None, tip = None, slot = None, 
                      checkable = False, duration = 2500, icon = None):

        action = QtGui.QAction(text, self.matplot_frame)

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
