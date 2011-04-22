#!/usr/bin/env python

import os, math, time

from PyQt4 import QtGui, QtCore
import networkx as NX
import matplotlib.pyplot as PLT
import numpy

class Graph(object):
    def __init__(self, parent=None, get_path=True):
        self.parent = parent
        self.status_bar = parent.status_bar
        
        self.artist = None
        self.axes = parent.axes
        self.ecolors = 'b'
        self.fig = parent.fig
        self.Gh = NX.Graph()
        self.node_sizes = []
        self.node_size_mult = (parent.node_size.value()/100.0)*1500 + 100
        self.objs = []
        self.pos = []
        self.selected = []
        self.selected_pos = []
    
        if get_path:
            # Dialog for step directory if not set
            if self.parent.step_path == None:
                filedialog = QtGui.QFileDialog()
                tmp = filedialog.getExistingDirectory(None, 'Open Directory', '')
                self.parent.set_step_path(str(tmp))
                os.chdir(self.parent.step_path)
            self.dirlist = os.listdir(self.parent.step_path)
    
    def center_on_node(self, node_name):
        '''sets the axis transform to fit the target node and it's neighbors
        Note: in co-occurrence and context graphs, this is essentially the same
        as center_on_graph, since these graphs are completely connected.'''
        
        # find neighbors of node
        neighbors = []
        neighbors.append(node_name)
        for e in self.Gh.edges():
            if e[0] == node_name or e[1] == node_name:
                if e[0] not in neighbors: neighbors.append(e[0])
                if e[1] not in neighbors: neighbors.append(e[1])
        
        # find most extreme values in all directions
        min_x = 10000; min_y = 10000;
        max_x = -10000; max_y = -10000;
        
        for n in neighbors:
            if self.pos[n][0] > max_x: max_x = self.pos[n][0]
            if self.pos[n][0] < min_x: min_x = self.pos[n][0]
            if self.pos[n][1] > max_y: max_y = self.pos[n][1]
            if self.pos[n][1] < min_y: min_y = self.pos[n][1]

        # create a small padding
        min_x -= .1*(max_x-min_x); min_y -= .1*(max_y-min_y);
        max_x += .1*(max_x-min_x); max_y += .1*(max_y-min_y);
        
        self.set_transform(min_x, min_y, max_x, max_y)
        
    def center_on_graph(self, node_name):
        #print self.pos[node_name][0], self.pos[node_name][1]
        print "coming soon"
        
    def destruct(self):
        '''Disconnects nodes listening for events that eat up cpu cycles.'''
        [o.disconnect() for o in self.nodes]
        
    def get_artist(self):
        '''Returns the current artist for the graph.'''
        return self.artist
    
    def graph_info(self):
        print "nodes: ", self.nodelist
    
    def is_step_file(self, fname):
        out = map(fname.endswith, ['.stp','.STP','.step','.STEP'])
        if any(out) == True: 
            return True
        return False
    
    def move_node(self, node_name, xpress, ypress, xdata, ydata):
        '''If the target node is not selected, or is the only selected node, move
        only that node. Else, move all nodes that are currently selected.'''
        if node_name in self.selected:
            for node,pos in zip(self.selected,self.selected_pos):
                self.pos[node][0] = pos[0] + (xdata - xpress)
                self.pos[node][1] = pos[1] + (ydata - ypress)
        else:
            self.pos[node_name][0] = xdata
            self.pos[node_name][1] = ydata
            
    def redraw(self, artist_fn=None, edges_fn=None, selected_fn=None):
        '''Redraws the current graph. Typically after a move or selection.'''
        #save transformations
        x1,x2 = self.axes.get_xlim()
        y1,y2 = self.axes.get_ylim()

        self.axes.clear()
        self.artist = None
        
        # Get all node positions
        try:
            xy=numpy.asarray([self.pos[v] for v in self.nodelist])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')
            
        # Get selected node positions
        try:
            ij=numpy.asarray([self.pos[v] for v in self.selected])
        except KeyError as e:
            raise nx.NetworkXError('Node %s has no position.'%e)
        except ValueError:
            raise nx.NetworkXError('Bad value in node positions.')
       
        # draw all the nodes by default
        if artist_fn:
            self.artist = artist_fn(xy, self.axes)
        else:
            self.artist = self.axes.scatter(xy[:,0], xy[:,1], self.node_size_mult, alpha=0.65) # default artist function
            
         # draw over the selected nodes with a new color, white by default
        if len(self.selected) > 0:
            # don't set self.artist for these scatter ()
            if selected_fn:
                selected_fn(ij, self.axes)
            else:
                # default selected function
                self.axes.scatter(ij[:,0], ij[:,1], self.node_size_mult, c='w', alpha=0.65) 
        
        # draw edges
        if edges_fn:
            self.edges = edges_fn(self.Gh, self.pos, self.axes)
        else:
            self.edges = NX.draw_networkx_edges(self.Gh, self.pos, ax=self.axes) # default edge function
        
        # draw node labels
        if self.parent.draw_node_labels_tf:
            NX.draw_networkx_labels(self.Gh, self.pos, ax=self.parent.axes, fontsize = 13)

        # restore transformations
        self.axes.set_xlim(x1,x2)
        self.axes.set_ylim(y1,y2)
        
        self.axes.grid(self.parent.draw_grid_tf)
        self.fig.canvas.draw()
        self.parent.setFocus(True)
            
    def save_selected_positions(self):
        '''Temporarily stores the positions of all selected nodes. These coords
        are needed to calculate the new positions during a move operation.'''
        self.selected_pos = []
        for node in self.selected:
            self.selected_pos.append([self.pos[node][0], self.pos[node][1]])
            
    def select_all(self):
        '''Select all nodes in the graph'''
        self.selected = [node.name for node in self.nodes]
        self.redraw()
            
    def select_inverse(self):
        '''Select all and only nodes that are not currently selected'''
        inverse = [node.name for node in self.nodes if node.name not in self.selected]
        self.selected = inverse
        self.redraw()
        
    def select_node(self, node_name, add = False):
        '''Deselects all selected nodes, and places the target into self.selected
        If add = True, places the target into self.selected with the other nodes'''
        if node_name == None:
            self.selected = []
        else:
            # Add the selected node to the current selected node list
            if add == True:
                if node_name not in self.selected:
                    self.selected.append(node_name)
                else:
                    self.selected.remove(node_name)
            
            # Unselect all currently selected, and select the indicated node
            else:
                if self.selected == [node_name]: self.selected = []
                else: self.selected = [node_name]      
        self.redraw()
        
    def select_none(self):
        self.select_node(None)
            
    def set_node_mult(self, mult):
        '''Used to decrease/increase the node size of a graph dynamically'''
        self.node_size_mult = (mult/100.0)*1500 + 100
        self.status_bar.showMessage('Node Size Multiplier: '+str(self.node_size_mult), 2500)
        self.redraw()
        
    def set_transform(self, min_x, min_y, max_x, max_y):
        '''transforms the axes to the coordinates input'''
        self.axes.set_xlim(min_x, max_x)
        self.axes.set_ylim(min_y, max_y)
        self.redraw()
            
            
        