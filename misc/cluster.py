import numpy, scipy
from numpy import random, array
from scipy import linalg

import matplotlib.pyplot as plt

n = 6
randperm = numpy.random.permutation(n)
gs = 2

group1 = randperm[0:gs+1];
group2 = randperm[gs:];

p_group1 = 0.5;
p_group2 = 0.4;
p_between = 0.1;

A = [[0]*n]*n

print A

for r,c in zip(group1, group1):
    print r,c
    A[r][c] = 0.5*(numpy.random.rand(gs, gs) < p_group1)

for r,c in zip(group2, group2):
    print r,c
    A[r][c] = 0.4*(numpy.random.rand(n-gs, n-gs) < p_group2)

for r,c in zip(group1, group2):
    A[r][c] = 0.3*(numpy.random.rand(gs, n-gs) < p_between)

for x in A[0]:
    print list(x)

#B = [list(x) for x in A[0][0]]
#print B

#C = numpy.triu(B, 1)


