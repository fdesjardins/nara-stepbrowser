import re
import os
import sys
import numpy, scipy
from numpy import random, array, triu, linalg
from scipy.sparse.linalg import eigs

from PyQt4 import QtGui
from PyQt4.QtGui import QDialog, QHBoxLayout

import networkx as NX
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.pylab as P

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def isStepFilename(f):
    return f.endswith('.stp') or f.endswith('.STP') or f.endswith('.step') or f.endswith('.STEP')

def _blob(x,y,area,color):
    hs = numpy.sqrt(area) / 2
    xcorners = numpy.array([x - hs, x + hs, x + hs, x - hs])
    ycorners = numpy.array([y - hs, y - hs, y + hs, y + hs])
    P.fill(xcorners, ycorners, color, edgecolor=color)

def flatten(lst):
    '''recursively flattens a nested list'''
    return sum( ([x] if not isinstance(x, list) else flatten(x)
                 for x in lst), [] )

def hinton(W, maxWeight=None):
    reenable = False
    if P.isinteractive():
        P.ioff()
    P.clf()
    height, width = W.shape
    if not maxWeight:
        maxWeight = 2**numpy.ceil(numpy.log(numpy.max(numpy.abs(W)))/numpy.log(2))

    P.fill(numpy.array([0,width,width,0]),numpy.array([0,0,height,height]),'gray')
    P.axis('off')
    P.axis('equal')
    for x in xrange(width):
        for y in xrange(height):
            _x = x+1
            _y = y+1
            w = W[y,x]
            if w > maxWeight/2:
                _blob(_x - 0.5, height - _y + 0.5, min(1,w/maxWeight),'white')
            elif w <= maxWeight/2:
                _blob(_x - 0.5, height - _y + 0.5, min(1,w/maxWeight),'black')
    if reenable:
        P.ion()
    P.show()

def index_tracker(A):
    fig = P.figure()
    ax = fig.add_subplot(111)
    tracker = IndexTracker(ax, A)
    P.show()

class IndexTracker:
    def __init__(self, ax, X):
        self.ax = ax
        self.X = X
        rows,cols = X.shape
        self.im = ax.imshow(self.X[:,:])
        self.im.set_data(self.X[:,:])
        self.im.axes.figure.canvas.draw()

def laplacian(A):
    '''returns combinatorial laplacian matrix of an array'''
    return (numpy.diag(sum(array(A), 2))-A)

def mk_assoc(A, groupA, groupB, p_val, r, mult=0.0):
    rand = mult*(r < p_val)
    rand = rand.tolist()
    tmp = flatten(rand)

    i=0
    for r in groupA:
        for c in groupB:
            A[r][c] = tmp[i]
            i += 1

    return A

def pprint(mat):
    '''pretty prints a 2d array'''
    out = ''
    for r in mat:
        for c in r:
            out += str(c) + '\t'
        out += '\n'
    print out

def sa_sort(lst):
    
    out = []
    for i in xrange(len(lst)):
        tmp = lst[0]
        for j in lst:
            if j**2 < tmp**2:
                tmp = j
        out.append(j)
    return out

basePath = os.curdir
app = QtGui.QApplication(sys.argv)
filedialog = QtGui.QFileDialog()
basePath = filedialog.getExistingDirectory(None, 'Open Directory', '')
basePath = str(basePath)
os.chdir(basePath)
dirlist = os.listdir(basePath)

stepdict = dict()

#print dirlist
#print("Building dictionary")


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
                        
    
#print term_lists
n = len(term_lists)

A = numpy.zeros((n,n))               
#find cooccurences using intersect
index1 = 0
nodes = []
for key1, value1 in term_lists.items():
    print index1, key1
    nodes.append(key1)
    index2 = 0
    for key2, value2 in term_lists.items():
        c = len(value1 & value2)
        A[index1, index2] = c
        A[index2, index1] = c
        index2 = index2 + 1
   	
    index1 = index1 + 1
	
print nodes

##### ----- Clustering ------ #####

B = triu(A, 1)
B += B.T

#index_tracker(A)
#index_tracker(B)

L = laplacian(B)

#index_tracker(L)

D,V = eigs(L, k=2, which='SR')

V2 = [x[1] for x in V]
_sorted = [x[1] for x in V]
_sorted.sort()

ind = [V2.index(x) for x in _sorted]
V_mag = [V[x] for x in ind]

print ind
#print V_mag


# Draw a line graph showing the cooccurence strengths
_draw = 0
if _draw == 1:
    print "drawing..."
    ax = plt.subplot(111)
    ax.plot([x[1] for x in V_mag], 'o-')
    # Attempting to set filenames in cooccurence strength graph
    i = 0
    v = 45
    for x in V_mag:
        ax.annotate(str(ind[i]), xy=(i, x[1]),  xycoords='data',
                    xytext=(0, v), textcoords='offset points',
                    arrowprops=dict(arrowstyle="->",
                                    connectionstyle="angle3,angleA=0,angleB=-90"),
                    )
        if v == 15:
            v = 45
        else:
            v -= 15
        i += 1
            
    plt.show()
	

# A_pp = A(p,p) in 1d array
A_pp = []
for x in ind:
    for y in ind:
        A_pp.append(A[x][y])
  
# out = A(p,p) in 2d array
out = scipy.zeros((n,n), float).tolist()
y = 0
for x in xrange(len(A_pp)):
    out[x%n][y] = A_pp[x]
    if (x+1)%n == 0:
        y += 1
     
#hinton(array(out), maxWeight = 0.5)
#index_tracker(array(out))

data = []

separators = [9]
clusters = len(separators)+1

# Create Matrices
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

print out
        

Ghs = []

for x in xrange(clusters):
    Ghs.append(NX.Graph(data=A))
    

'''
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
NX.draw_networkx_edges(Gh, position, Gh.edges(), width=1.0, alpha=0.75, edge_color = ecolors, edge_cmap=plt.cm.Blues, edge_vmin = A.min(), edge_vmax = A.max())
NX.draw_networkx_labels(Gh, position, fontsize = 14)
# now for the Matplotlib part:
plt.axis("off")
plt.show()
'''    
