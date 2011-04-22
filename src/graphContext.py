#!/usr/bin/env python

import os, re

import networkx as NX
import matplotlib.pyplot as PLT

import numpy, scipy
from numpy import random, array, triu, linalg
from scipy.sparse.linalg import eigs

from draggableNode import DraggableNode
from graph import Graph

class GraphContext(Graph):
    def __init__(self, parent = None):
        Graph.__init__(self, parent)
        
        # Build dictionary and term_list for each file in current dir
        step_dict = dict()
        term_lists = dict()
        for f in self.dirlist:
            if os.path.isfile(os.path.join(self.parent.step_path, f)) and self.is_step_file(f):
                step_dict, term_lists = self.build_dict(f, step_dict, term_lists)

        # Create an nxn matrix containing term co-occurrence strengths
        n = len(term_lists)
        A = numpy.zeros((n,n))
        self.A = self.find_cooccurrences(A, term_lists)

        self.ind, self.mag = self.indices(self.A) # Indices and magnitudes of files
        self.separators = self.best_separation(self.ind, self.mag)

        cl_matrices = self.cluster(self.A, self.ind, self.separators)
        
        Ghs = self.gen_graphs(cl_matrices) # Temporary graphs, used to gather edge lists

        # Temporary nodes+edges
        nodes = [key for key,value in term_lists.items()]
        edges = [g.edges() for g in Ghs]
        
        # Each graph returns edges referencing nodes 0..n from graph.edges() above.
        # Thus, if there are multiple independent graphs, we need to adjust indices
        # such that they are appropriate for describing the list of all nodes
        edges = self.unpack_edges(edges)

        # Create real nodes+edges, using draggable nodes
        self.edges = [(nodes[e[0]], nodes[e[1]]) for e in edges]
        self.ecolors = [A[node[0], node[1]] for node in edges]
        self.nodes = [DraggableNode(self,x) for x in nodes]

        # May have to engineer something here. Have 2 options:
        # 1) Rename each duplicate node reference from the edge list
        #    and change the structure of draggable node

        # 2) Draw separate graphs for each cluster
        #      - Tabs, Windows, Split the frame

        # Create graph and add nodes+edges
        [self.Gh.add_node(x, obj=n) for x,n in zip(nodes, self.nodes)]
        [self.Gh.add_edge(e[0], e[1], weight = w) for e,w in zip(self.edges, self.ecolors)]
        self.nodelist = self.Gh.nodes()
        
        self.pos = NX.spring_layout(self.Gh)

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

        # Generate scatter graph, draw edges and labels
        self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, c='b', alpha=0.5)
        self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes, width=1.0, alpha=.75, edge_color=self.ecolors,
                                            edge_cmap=PLT.cm.Blues, edge_vmin = self.A.min(), edge_vmax = self.A.max())
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)
            
            
    def best_separation(self, ind, mag):
        '''Determines the best place to segment the indices into
        two clusters based on the magnitudes returned from eigs'''

        if mag[0][1] < 0+0.j:
            for v in xrange(len(mag)):
                if mag[v][1] > 0+0.j:
                    break
        else:
            for v in xrange(len(mag)):
                if mag[v][1] < 0+0.j:
                    break
        return [v]

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

    def check_directory(self):
        '''Dialog for step directory if not set'''
        if self.parent.step_path == None:
            filedialog = QtGui.QFileDialog()
            tmp = filedialog.getExistingDirectory(None, 'Open Directory', '')
            self.parent.set_step_path(str(tmp))
            os.chdir(self.parent.step_path)

    def cluster(self, A, ind, separators):
        '''Returns a list of 1d lists, representing clustered portions of the matrix A using
        the supplied separators and indices''' 
        clusters = len(separators) + 1
        out = []
        for s in xrange(clusters):
            tmp = []
            
            if s == 0:
                for i in ind[0:separators[s]]:
                    for j in ind[0:separators[s]]:
                        tmp.append(A[i][j])
                out.append(tmp)

            elif s == len(separators):
                for i in ind[separators[s-1]:]:
                    for j in ind[separators[s-1]:]:
                        tmp.append(A[i][j])
                out.append(tmp)

            else: 
                for i in ind[separators[s-1]:separators[s]]:
                    for j in ind[separators[s-1]:separators[s]]:
                        tmp.append(A[i][j])
                out.append(tmp)
        return out
    
    def find_cooccurrences(self, A, term_lists):
        '''Returns a matrix containing strength of term cooccurrence between every STEP file input'''
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

    def flatten(self, lst):
        '''recursively flattens a nested list'''
        return sum( ([x] if not isinstance(x, list) else self.flatten(x)
                     for x in lst), [] )

    def gen_graphs(self, ms):
        '''Returns a list of networkx graphs, representing clusters of a larger graph'''

        # Convert each matrix in ms to 2d arrays
        arrays = []
        for m in ms:
            _n = int(len(m)**(1/2.0))
            tmp = scipy.zeros((_n,_n), float).tolist()
            y=0
            for x in xrange(len(m)):
                tmp[x%_n][y] = m[x]
                if (x+1)%_n == 0:
                    y += 1
            arrays.append(array(tmp))

        return [NX.Graph(data=a) for a in arrays]
        
    def indices(self, A):
        '''Returns the indices of files in , with a '/' in place where the files represented in A
        should be split to form independent graphs. Also returns the list of magnitudes in order.'''
        
        _A = triu(A, 1) # Upper triangle
        _A += _A.T # += Transpose

        def laplacian(A):
            '''returns combinatorial laplacian matrix of an array'''
            return (numpy.diag(sum(array(A), 2))-A)

        L = laplacian(_A)

        D,V = eigs(L, k=2, which='SR') # two smallest reals

        V2 = [x[1] for x in V]
        V_sorted = [x[1] for x in V]
        V_sorted.sort()

        ind = [V2.index(x) for x in V_sorted]
        V_mag = [V[x] for x in ind]

        return ind, V_mag
    
    def redraw(self):
        '''Redraws the current graph. Typically after a move or selection.'''
        
        # Need to specify the functions for drawing artist (nodes) and edges during redraw
        def artist_fn(xy, axes):
            return self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, alpha=0.5)
        def edges_fn(g, pos, axes, ecolor='red'):
            return NX.draw_networkx_edges(g, pos, ax=axes, width=1.0, alpha=.75, edge_color=self.ecolors, 
                                          edge_cmap=PLT.cm.Blues, edge_vmin = self.A.min(), edge_vmax = self.A.max())
            
        super(GraphCoOccurrence, self).redraw(artist_fn, edges_fn)
    
    def unpack_edges(self, edges, out = None):
        '''Recursively organizes edges'''
        
        if edges == []:
            return out
        
        elif out == None:
            out = edges[0]
            return self.unpack_edges(edges[1:], out)
        
        else:
            m = 0
            for e in out: 
                if e[0] > m: m = e[0]
                if e[1] > m: m = e[1]
                
            tmp = []
            for e in edges[0]:
                tmp.append((e[0]+m+1, e[1]+m+1))
            return self.unpack_edges(edges[1:], out+tmp)