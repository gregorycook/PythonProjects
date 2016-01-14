from orthogonalization import orthogonalize
from orthogonalization import aug_orthogonalize
from vec import Vec
from math import sqrt
from matutil import coldict2mat
from matutil import mat2coldict
from mat import transpose


def orthonormalize(L):
    '''
    Input: a list L of linearly independent Vecs
    Output: A list T of orthonormal Vecs such that for all i in [1, len(L)],
            Span L[:i] == Span T[:i]
    '''
    orth = orthogonalize(L)
    return [v/sqrt(v*v) for v in orth]


def aug_orthonormalize(L):
    '''
    Input:
        - L: a list of Vecs
    Output:
        - A pair Qlist, Rlist such that:
            * coldict2mat(L) == coldict2mat(Qlist) * coldict2mat(Rlist)
            * Qlist = orthonormalize(L)
    '''
    Q=orthonormalize(L)
    ##print("1--------------")
    ##print(Q)
    Rdict = mat2coldict(transpose(coldict2mat(Q))*coldict2mat(L))
    R = [Rdict[k] for k in Rdict]
    ##print("2--------------")
    ##print(R)
    ##print("--------------2")
    return Q,R


