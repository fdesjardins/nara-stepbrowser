from PyQt4 import QtGui
from PyQt4.QtGui import QDialog, QVBoxLayout, QTextEdit

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

class ClusteringConfig(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self)
        
        self.parent = parent
        self.g = self.parent.matplot_frame.g
        
        self.setWindowTitle('Clustering Configuration')
        
        #MPL figure
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
        
        #QT canvas
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('pick_event', self.on_pick) #used when selecting canvas objects
        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False) #clear the axes every time plot() is called

        #MPL Toolbar
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        
        vbox=QVBoxLayout(self)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        
        self.setLayout(vbox)
        self.resize(650,350)

    def on_pick(self):
        print 'picked in clustering config'

    def _show(self):
        self.axes.clear()
        self.g = self.parent.matplot_frame.g
        self.axes.plot([x[1] for x in self.g.mag], 'o-')
        i = 0
        v = 45
        for x in self.g.mag:
            self.axes.annotate(str(self.g.ind[i]), xy=(i, x[1]), xycoords='data',
                        xytext=(0, v), textcoords='offset points',
                        arrowprops=dict(arrowstyle="->",
                                        connectionstyle="angle3,angleA=0,angleB=-90"),
                                   )
            if v == 15:
                v = 45
            else:
                v -= 15
            i += 1
            
        self.show()
