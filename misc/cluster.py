import numpy, scipy
from numpy import random, array, triu, linalg
from scipy.sparse.linalg import eigs

import matplotlib.pyplot as plt
import matplotlib.pylab as P

def main():

    n = 1000

    randperm = random.permutation(n)
    gs = 350
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
    
    L = laplacian(A)

    D,V = eigs(L, k=2, which='SR')

    V2 = [x[1] for x in V]
    _sorted = [x[1] for x in V]
    _sorted.sort()

    ind = [V2.index(x) for x in _sorted]
    V_jump = [V[x] for x in ind]

    #ax = plt.subplot(111)
    #ax.plot([x[1] for x in V_jump])
    #plt.show()

    # A(p,p) in 1d array
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
    index_tracker(array(out))
    

# def eigs(L, k, sigma):

#     D,V = linalg.eig(L)
#     print V
#     print D
#     D_out = 0

#     if sigma == 'SA':
#         x = range(0, len(V[0]))
#         lst = []
#         for r,c in zip(x,x):
#             lst.append(V[r][c])

#         lst.sort()
        
#         V_out = numpy.diag(lst[:k])

#         return V_out, D_out

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

if __name__ == '__main__':
    main()

