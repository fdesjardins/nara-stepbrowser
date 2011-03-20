import re
import os
import sys
import numpy as N
import networkx as NX
import matplotlib.pyplot as PLT
from PyQt4 import QtGui

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def isStepFilename(f):
    return f.endswith('.stp') or f.endswith('.STP') or f.endswith('.step') or f.endswith('.STEP')

basePath = os.curdir
app = QtGui.QApplication(sys.argv)
filedialog = QtGui.QFileDialog()
basePath = filedialog.getExistingDirectory(None, 'Open Directory', '')
basePath = str(basePath)
os.chdir(basePath)
dirlist = os.listdir(basePath)

stepdict = dict()

print dirlist
print("Building dictionary")


term_lists = dict()
for f in dirlist:
    if os.path.isfile(os.path.join(basePath, f)) and isStepFilename(f):
        #print(f)
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
                            if token in stepdict:
                                stepdict[token] = stepdict[token] + 1
                            else:
                                stepdict[token] = 1
                        
       
    
print term_lists
n = len(term_lists)

A = N.zeros((n,n))               
#find cooccurences using intersect
index1 = 0
for key1, value1 in term_lists.items():
    print index1, key1
    index2 = 0
    for key2, value2 in term_lists.items():
        c = len(value1 & value2)
        A[index1, index2] = c
        A[index2, index1] = c
        index2 = index2 + 1
        
    index1 = index1 + 1
    
Gh = NX.Graph(data=A)
all_nodes = Gh.nodes()
edges = Gh.edges()
ecolors = [A[node[0], node[1]] for node in edges]

# to scale node size with degree:
scaled_node_size = lambda(node) : NX.degree(Gh, node) * 15
#position = NX.circular_layout(Gh)    # just choose a layout scheme
position = NX.spring_layout(Gh)    # just choose a layout scheme
#position = NX.shell_layout(Gh)    # just choose a layout scheme
NX.draw_networkx_nodes(Gh, position, node_size=map(scaled_node_size, all_nodes), node_color='b', alpha = 0.75)
NX.draw_networkx_edges(Gh, position, Gh.edges(), width=1.0, alpha=0.75, edge_color = ecolors, edge_cmap=PLT.cm.Blues, edge_vmin = A.min(), edge_vmax = A.max())
NX.draw_networkx_labels(Gh, position, fontsize = 14)
# now for the Matplotlib part:
PLT.axis("off")
PLT.show()
    
