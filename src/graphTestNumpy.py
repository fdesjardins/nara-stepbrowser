import networkx as NX
import matplotlib.text as text
import numpy

class GraphTestNumPy(object):
    def __init__(self, parent = None):
        self.parent = parent

        n = 100
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
        A = A + A.transpose()
        adj = numpy.array(A)
        Gh = NX.Graph(data=adj)
        all_nodes = Gh.nodes()
        # to scale node size with degree:
        scaled_node_size = lambda(node) : NX.degree(Gh, node) * 7
        position = NX.spring_layout(Gh)    # just choose a layout scheme
        NX.draw_networkx_nodes(Gh, position, ax=self.parent.axes, node_size=map(scaled_node_size, all_nodes))
        NX.draw_networkx_edges(Gh, position, ax=self.parent.axes, width=1.0, alpha=1.0, edge_color="red")
