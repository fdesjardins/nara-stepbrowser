#!/usr/bin/env python

import networkx as NX
import numpy

from draggableNode import DraggableNode
from graph import Graph

class GraphTest(Graph):
    def __init__(self, parent = None):
        Graph.__init__(self, parent, False)
        
        files = ['file'+str(x)+'.step' for x in xrange(5)]
        self.nodes = [DraggableNode(self, x) for x in files]

        [self.Gh.add_node(x, obj=n) for x,n in zip(files, self.nodes)]
        [self.Gh.add_edge(files[0], files[x], weight=x*1.0) for x in xrange(1,5)]
        [self.Gh.add_edge(files[4], files[x], weight=x*1.0) for x in xrange(0,4)]
        self.nodelist = self.Gh.nodes()

        self.pos = NX.spring_layout(self.Gh)

        try:
            xy=numpy.asarray([self.pos[v] for v in self.nodelist])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')

        # DraggableNode order is not garaunteed coming out of the NX.spring_layout
        # call, because it returns a hashtable. Here, we make sure each node is 
        # correctly numbered.
        for o in self.nodes:
            o.set_node_num(o, self.nodelist.index(o.name))

        scaled_node_size = lambda(node) : NX.degree(self.Gh, node) * self.node_size_mult
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, alpha=0.65)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes)
        
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)