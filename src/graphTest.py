#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox

import networkx as NX
import matplotlib.text as text
import numpy

from draggableNode import DraggableNode

class GraphTest(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.status_bar = parent.status_bar
        self.axes = parent.axes
        self.fig = parent.fig
        self.node_size_mult = 700
        
        self.g = NX.Graph()

        files = ['file'+str(x)+'.step' for x in xrange(15)]
        self.objs = [DraggableNode(self, x) for x in files]

        [self.g.add_node(x, obj=n) for x,n in zip(files, self.objs)]
        [self.g.add_edge(files[0], files[x], weight=x*1.0) for x in xrange(1,15)]
        [self.g.add_edge(files[14], files[x], weight=x*1.0) for x in xrange(0,14)]
        nodelist = self.g.nodes()

        self.pos = NX.spring_layout(self.g)

        try:
            xy=numpy.asarray([self.pos[v] for v in nodelist])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')

        # DraggableNode order is not garaunteed coming out of the NX.spring_layout
        # call, because it returns a hashtable. Here, we make sure each node is 
        # correctly numbered.
        for o in self.objs:
            o.set_node_num(o, nodelist.index(o.name))

        scaled_node_size = lambda(node) : NX.degree(self.g, node) * self.node_size_mult
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult)
        self.edges = NX.draw_networkx_edges(self.g, self.pos, ax=self.axes)

    def destruct(parent, self):
        '''Disconnects nodes listening for events that eat up cpu cycles'''
        [o.disconnect(o) for o in self.objs]

    def get_artist(child, self):
        return self.artist

    def set_node_mult(self, mult):
        self.node_size_mult = (mult/100.0)*1500 + 100
        self.status_bar.showMessage('Node Size Multiplier: '+str(self.node_size_mult), 2500)
        self.redraw(self)

    def redraw(caller, self):

        #save transformations
        x1,x2 = self.axes.get_xlim()
        y1,y2 = self.axes.get_ylim()

        self.axes.clear()
        self.artist = None

        try:
            xy=numpy.asarray([self.pos[v] for v in self.g.nodes()])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')

        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult)
        self.edges = NX.draw_networkx_edges(self.g, self.pos, ax=self.axes)

        self.axes.set_xlim(x1,x2)
        self.axes.set_ylim(y1,y2)
        
        self.axes.grid(self.parent.draw_grid_tf)
        self.fig.canvas.draw()
        

class GraphTestOld(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.axes = parent.axes
        self.artist = None
        
        self.g = NX.Graph()
        self.g.add_node(3)
        self.g.add_node(DraggableNode(self, "node0"))
        self.g.add_node(DraggableNode(self, "node1"))
        self.g.add_node(DraggableNode(self, "node2"))
        self.g.add_node(DraggableNode(self, "node3"))
        pos = NX.spring_layout(self.g)
        self.parent.axes.set_axis_off()
        nodes = self.g.nodes()
        print nodes
        #dnodes = [DraggableNode(node) for node in nodes]

        scaled_node_size = lambda(node) : NX.degree(self.g, node) * 700
        self.artist = NX.draw_networkx_nodes(self.g, pos, ax=self.parent.axes, nodelist=nodes, node_shape='^')
        print "Artist: ", self.artist
        self.artist.set_picker(5)
        self.artist.findobj()
        NX.draw_networkx_edges(self.g, pos, ax=self.parent.axes)

        print self.g[3]

    def get_artist(self, gt):
        return gt.artist
