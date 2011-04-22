import networkx as NX
import matplotlib.text as text
import matplotlib.pyplot as PLT
import numpy, scipy

from graph import Graph
from draggableNode import DraggableNode

class GraphTestNumPy(Graph):
    def __init__(self, parent = None):
        Graph.__init__(self, parent, False)
        self.parent = parent
        n = 50
        x = numpy.random.permutation(range(0,n))
        gs = 35
        group1 = x[0:gs]
        group2 = x[gs:]
        p_group1 = 0.5
        p_group2 = 0.4
        p_between = 0.1
        A = numpy.zeros([n,n])
        A[numpy.ix_(group1, group1)] = 0.5*(numpy.random.rand(gs,gs) < p_group1)
        A[numpy.ix_(group2, group2)] = 0.4*(numpy.random.rand(n-gs,n-gs) < p_group2)
        A[numpy.ix_(group1, group2)] = 0.3*(numpy.random.rand(gs,n-gs) < p_between)
        A = numpy.triu(A,1)
        self.A = A + A.transpose()
        adj = numpy.array(self.A)
        self.Gh = NX.Graph(data=adj)
        nodes = self.Gh.nodes()
        edges = self.Gh.edges()
        self.ecolors = [A[node[0], node[1]] for node in edges]
        self.nodes = [DraggableNode(self,node) for node in self.Gh.nodes()]
        self.edges = [(nodes[e[0]], nodes[e[1]]) for e in self.Gh.edges()]
        self.Gh = NX.Graph()
        [self.Gh.add_node(x, obj=n) for x,n in zip(self.Gh.nodes(), self.nodes)]
        [self.Gh.add_edge(e[0], e[1]) for e in self.edges]
        self.pos = NX.spring_layout(self.Gh)
        self.nodelist = self.Gh.nodes()
        
        try:
            # Array of xy positions of every node in nodelist
            xy=numpy.asarray([self.pos[v] for v in self.nodelist])
        except KeyError as e:
            raise NX.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise NX.NetworkXError('Bad value in node positions.')

        # DraggableNode order is not garaunteed coming out of the NX.spring_layout
        # call, because it returns a hashtable. Here, we make sure each node is 
        # correctly numbered.
        for o in self.nodes:
            o.set_node_num(o, self.nodelist.index(o.name))
            
        self.scaled_node_size = lambda(node) : NX.degree(self.Gh, node)**(1/2.0) * (1/2.0) * self.node_size_mult
        self.node_sizes = map(self.scaled_node_size, self.nodelist)
            
        # Generate scatter graph, draw edges and labels
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_sizes, alpha=0.6) # default artist function
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, width=1.0, alpha=.75, edge_color=self.ecolors,
                                            edge_cmap=PLT.cm.Blues, edge_vmin = self.A.min(), edge_vmax = self.A.max())
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)
            
    def redraw(self):
        '''Redraws the current graph. Typically after a move or selection.'''
        
        # create new node size list for selected nodes
        selected_sizes = map(self.scaled_node_size, self.selected)
        
        # Need to specify the functions for drawing artist (nodes) and edges during redraw
        def artist_fn(xy, axes):
            return self.axes.scatter(xy[:,0], xy[:,1], self.node_sizes, alpha=0.6)
        def edges_fn(g, pos, axes, ecolor='red'):
            return NX.draw_networkx_edges(g, pos, ax=axes, width=1.0, alpha=.75, edge_color=self.ecolors, 
                                          edge_cmap=PLT.cm.Blues, edge_vmin = self.A.min(), edge_vmax = self.A.max())
        def selected_fn(xy, axes, color='w', _alpha=0.65):
            return axes.scatter(xy[:,0], xy[:,1], selected_sizes, c=color, alpha=_alpha)
            
        super(GraphTestNumPy, self).redraw(artist_fn, edges_fn, selected_fn)
        
    def set_node_mult(self, mult):
        '''Used to decrease/increase the node size of a graph dynamically'''
        self.node_size_mult = (mult/100.0)*1500 + 100
        self.node_sizes = map(self.scaled_node_size, self.nodelist)
        self.status_bar.showMessage('Node Size Multiplier: '+str(self.node_size_mult), 2500)
        self.redraw()
        