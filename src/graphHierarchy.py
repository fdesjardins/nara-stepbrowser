#!/usr/bin/env python

import os, re

import networkx as NX

import matplotlib.pyplot as PLT

import numpy, scipy
from numpy import random, array, triu, linalg
from scipy.sparse.linalg import eigs

from draggableNode import DraggableNode
from graph import Graph

class GraphHierarchy(Graph):
    def __init__(self, parent = None):
        Graph.__init__(self, parent)
        
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

        self.nodelist = self.Gh.nodes()

        self.pos = NX.spring_layout(self.Gh,scale=10)

        try:
            xy=numpy.asarray([self.pos[v] for v in self.nodelist])
        except KeyError as e:
            raise NX.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise NX.NetworkXError('Bad value in node positions.')

        # DraggableNode order is not gauranteed coming out of the NX.spring_layout
        # call, because it returns a hashtable. Here, we make sure each node is 
        # correctly numbered.
        [o.set_node_num(o, self.nodelist.index(o.name)) for o in self.nodes]

        self.scaled_node_size = lambda(node) : NX.degree(self.Gh, node)**(1/2.0) * self.node_size_mult
        self.node_sizes = map(self.scaled_node_size, self.nodelist)
        
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_sizes, c='r', alpha=0.5)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, width=1.0, alpha=1.0, edge_color="red")        
       
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)
            
    def find_edges(self, f, dirlist, xref_str, doc_str):
        '''Parses a file for link to other STEP files, returning corresponding graph edges'''
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
    
    def redraw(self):
        '''Redraws the current graph. Typically after a move or selection.'''
        
        # create new node size list for selected nodes
        selected_sizes = map(self.scaled_node_size, self.selected)
        
        # Need to specify the functions for drawing artist (nodes) and edges during redraw
        def artist_fn(xy, axes, color='r', _alpha=0.5):
            return axes.scatter(xy[:,0], xy[:,1], self.node_sizes, c=color, alpha=_alpha)
        def edges_fn(g, pos, axes, ecolor='red'):
            return NX.draw_networkx_edges(g, pos, ax=axes, edge_color=ecolor)
        def selected_fn(xy, axes, color='w', _alpha=0.65):
            return axes.scatter(xy[:,0], xy[:,1], selected_sizes, c=color, alpha=_alpha)
            
        super(GraphHierarchy, self).redraw(artist_fn, edges_fn, selected_fn)
        
    def set_node_mult(self, mult):
        '''Used to decrease/increase the node size of a graph dynamically'''
        self.node_size_mult = (mult/100.0)*1500 + 100
        self.node_sizes = map(self.scaled_node_size, self.nodelist)
        self.status_bar.showMessage('Node Size Multiplier: '+str(self.node_size_mult), 2500)
        self.redraw()
            
            
            