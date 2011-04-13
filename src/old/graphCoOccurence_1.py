#!/usr/bin/env python

import re, os

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox

import matplotlib.pyplot as PLT
import networkx as NX
import numpy

from draggableNode import DraggableNode

class GraphCoOccurence1(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.status_bar = parent.status_bar
        self.axes = parent.axes
        self.fig = parent.fig
        self.node_size_mult = 700

        # Dialog for step directory if not set
        if self.parent.step_path == None:
            filedialog = QtGui.QFileDialog()
            tmp = filedialog.getExistingDirectory(None, 'Open Directory', '')
            self.parent.set_step_path(str(tmp))
            os.chdir(self.parent.step_path)

        dirlist = os.listdir(self.parent.step_path)

        # Build dictionary and term_list for each file in current dir
        step_dict = dict()
        term_lists = dict()
        for f in dirlist:
            if os.path.isfile(os.path.join(self.parent.step_path, f)) and self.is_step_file(f):
                step_dict, term_lists = self.build_dict(f, step_dict, term_lists)

        n = len(term_lists)
        A = numpy.zeros((n,n))
        self.A = self.find_cooccurences(A, term_lists)
        gh = NX.Graph(data=self.A) # Used to gather edge list

        # Temporary nodes/edges from graph gh
        nodes = [key for key,value in term_lists.items()]
        edges = gh.edges()

        # Create real nodes and edges, using draggable nodes
        self.edges = [(nodes[e[0]], nodes[e[1]]) for e in gh.edges()]
        self.nodes = [DraggableNode(self,x) for x in nodes]
        self.ecolors = [A[node[0], node[1]] for node in edges]
        
        # Create graph and add real nodes/edges
        self.Gh = NX.Graph()
        [self.Gh.add_node(x, obj=n) for x,n in zip(nodes, self.nodes)]
        [self.Gh.add_edge(e[0], e[1], weight = w) for e,w in zip(self.edges, self.ecolors)]

        nodelist = self.Gh.nodes()
        self.pos = NX.spring_layout(self.Gh)

        try:
            xy=numpy.asarray([self.pos[v] for v in nodelist])
        except KeyError as e:
            raise NX.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise NX.NetworkXError('Bad value in node positions.')

        # DraggableNode order is not gauranteed coming out of the NX.spring_layout
        # call, because it returns a hashtable. Here, we make sure each node is 
        # correctly numbered.
        for o in self.nodes:
            o.set_node_num(o, nodelist.index(o.name))

        # Generate scatter graph, draw edges and labels
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, c='b', alpha=0.65)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, width=1.0, alpha=.75, edge_color=self.ecolors,
                                            edge_cmap=PLT.cm.Blues, edge_vmin = self.A.min(), edge_vmax = self.A.max())
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)
            
    def destruct(parent, self):
        '''Disconnects nodes from listening in the current frame'''
        [o.disconnect() for o in self.nodes]
            
    def build_dict(self, f, step_dict, term_lists):
        '''Accepts a file, dictionary of terms, and dictionary of STEP files
        and adds new terms and the file f to each dictionary'''
        term_lists[f] = set()
        for line in open(f):
            line_parts = line.split("'")
            for i in range(1,len(line_parts),2):
                string = line_parts[i]
                if string != '' and string[0] != '#':

                    tokens = re.split('\W+', string)
                    for token in tokens:
                        if token != '':
                            term_lists[f].add(token)
                            if token in step_dict:
                                step_dict[token] = step_dict[token] + 1
                            else:
                                step_dict[token] = 1
        return step_dict, term_lists

    def find_cooccurences(self, A, term_lists):
        index1 = 0
        for key1, value1 in term_lists.items():
            #print index1, key1
            index2 = 0
            for key2, value2 in term_lists.items():
                c = len(value1 & value2)
                A[index1, index2] = c
                A[index2, index1] = c
                index2 = index2 + 1
            index1 = index1 + 1
        return A

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
            raise NX.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise NX.NetworkXError('Bad value in node positions.')

        # Generate scatter graph, draw edges and labels
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, c='b', alpha=0.65)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, width=1.0, alpha=.75, edge_color=self.ecolors,
                                            edge_cmap=PLT.cm.Blues, edge_vmin = self.A.min(), edge_vmax = self.A.max())
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)

        # restore transformations
        self.axes.set_xlim(x1,x2)
        self.axes.set_ylim(y1,y2)
        
        self.axes.grid(self.parent.draw_grid_tf)
        self.fig.canvas.draw()

    def set_node_mult(self, mult):
        self.node_size_mult = (mult/100.0)*1500 + 100
        self.status_bar.showMessage('Node Size Multiplier: '+str(self.node_size_mult), 2500)
        self.redraw(self)
