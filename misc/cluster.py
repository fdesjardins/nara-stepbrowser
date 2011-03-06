import numpy, scipy
from numpy import random, array, triu, linalg
from scipy import zeros

from decimal import Decimal

import matplotlib.pylab as P

def main():

    n = 100

    randperm = random.permutation(n)
    gs = 35
    group1 = randperm[0:gs]
    group2 = randperm[gs:]

    p_group1 = 0.5
    p_group2 = 0.4
    p_between = 0.1

    A = scipy.zeros((n,n), float).tolist()
    A = mk_assoc(A, group1, group1, p_group1, random.rand(gs,gs), mult=0.5)
    A = mk_assoc(A, group2, group2, p_group2, random.rand(n-gs,n-gs), mult=0.4)
    A = mk_assoc(A, group1, group2, p_between,random.rand(gs,n-gs), mult=0.3)
    A = triu(A, 1)
    A += A.T

    #hinton(A, maxWeight = 0.5)
    #index_tracker(A)
    
    L = laplacian(A);

    V, D = eigs(L, 2, 'SA')

def eigs(L, k, sigma):

    [V,D] = linalg.eig(L)

    if sigma == 'SA':
        x = range(0, len(D[0]))
        lst = []
        for r,c in zip(x,x):
            lst.append(D[r][c])

        lst.sort()
        return 0, numpy.diag(lst[:k])

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

if __name__ == '__main__':
    main()

