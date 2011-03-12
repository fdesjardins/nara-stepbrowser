#!/usr/bin/env python

import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QFileDialog, QMessageBox

import networkx as NX
import matplotlib.text as MLtext
import numpy

from draggableNode import DraggableNode

class GraphHierarchy1(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.status_bar = parent.status_bar
        self.axes = parent.axes
        self.fig = parent.fig
        self.node_size_mult = 700

        # Dialog for step directory if not set
        print self.parent.step_path
        if self.parent.step_path == None:
            filedialog = QtGui.QFileDialog()
            tmp = filedialog.getExistingDirectory(None, 'Open Directory', '')
            self.parent.set_step_path(str(tmp))
            os.chdir(self.parent.step_path)

        self.Gh = NX.Graph()
        
        dirlist = os.listdir(self.parent.step_path)
        xref_str = "APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT"
        doc_str = "DOCUMENT_FILE"
        
        edges = []
        for f in os.listdir(self.parent.step_path):
            if os.path.isfile(os.path.join(self.parent.step_path, f)) and self.is_step_file(f):
                edges += self.find_edges(f, dirlist, xref_str, doc_str)

        nodes = []
        for e in edges:
            if e[0] not in nodes: nodes.append(e[0])
            if e[1] not in nodes: nodes.append(e[1])

        self.nodes = [DraggableNode(self, x) for x in nodes]
        [self.Gh.add_node(x, obj=n) for x,n in zip(nodes, self.nodes)]
        [self.Gh.add_edge(e[0], e[1]) for e in edges]

        nodelist = self.Gh.nodes()

        self.pos = NX.spring_layout(self.Gh)

        try:
            xy=numpy.asarray([self.pos[v] for v in nodelist])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')

        # DraggableNode order is not garaunteed coming out of the NX.spring_layout
        # call, because it returns a hashtable. Here, we make sure each node is 
        # correctly numbered.
        for o in self.nodes:
            o.set_node_num(o, nodelist.index(o.name))

        scaled_node_size = lambda(node) : NX.degree(self.Gh, node) * self.node_size_mult
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, c='r', alpha=0.5)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, width=1.0, alpha=1.0, edge_color="red")        
       
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 14)
        
    def destruct(parent, self):
        '''Disconnects nodes listening for events that eat up cpu cycles'''
        [o.disconnect(o) for o in self.nodes]

    def find_edges(self, f, dirlist, xref_str, doc_str):
        out = []
        for line in open(f):
            if xref_str in line:
                line_parts = line.split("'")
                if len(line_parts) > 2:
                    xref_name = line_parts[1]
                    
                    try:
                        (xref_name for xref_name in dirlist).next()
                        #print(f, " -> ", xref_name)
                        out.append([f,xref_name])
                    except:
                        print("File ", f, " references xref ", xref_name, ", but that xref does not exist.")
        return out

    def find_step_files(self):
        out = []
        for root, dirs, _files in os.walk(self.parent.step_path):
            # print root, dirs, files
            for f in _files:
                if self.isStepFilename(f):
                    out.append(os.path.join(root, f))
        return out

    def get_artist(child, self):
        return self.artist

    def is_step_file(self, fname):
        out = map(fname.endswith, ['.stp','.STP','.step','.STEP'])
        if any(out) == True: 
            return True
        return False

    def redraw(caller, self):

        # save transformations
        x1,x2 = self.axes.get_xlim()
        y1,y2 = self.axes.get_ylim()

        self.axes.clear()
        self.artist = None

        try:
            xy=numpy.asarray([self.pos[v] for v in self.Gh.nodes()])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')

        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, c='r', alpha=0.5)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, edge_color='red')

        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 14)

        # restore transformations
        self.axes.set_xlim(x1,x2)
        self.axes.set_ylim(y1,y2)
        
        self.axes.grid(self.parent.draw_grid_tf)
        self.fig.canvas.draw()

    def set_node_mult(self, mult):
        self.node_size_mult = (mult/100.0)*1500 + 100
        self.status_bar.showMessage('Node Size Multiplier: '+str(self.node_size_mult), 2500)
        self.redraw(self)
