from vec import Vec
from mat import Mat
from solver import solve

def identity(D, one):
  """Given a set D and the field's one, returns the DxD identity matrix
  e.g.:
  
  >>> identity({0,1,2}, 1)
  Mat(({0, 1, 2}, {0, 1, 2}), {(0, 0): 1, (1, 1): 1, (2, 2): 1})
  """
  return Mat((D,D), {(d,d):1 for d in D})

def keys(d):
  """Given a dict, returns something that generates the keys; given a list,
     returns something that generates the indices.  Intended for coldict2mat and rowdict2mat.
  """
  return d.keys() if isinstance(d, dict) else range(len(d))

def value(d):
  """Given either a dict or a list, returns one of the values.
     Intended for coldict2mat and rowdict2mat.
  """
  return next(iter(d.values())) if isinstance(d, dict) else d[0]

def mat2rowdict(A):
  """Given a matrix, return a dictionary mapping row labels of A to rows of A
	 e.g.:
	 
     >>> M = Mat(({0, 1, 2}, {0, 1}), {(0, 1): 1, (2, 0): 8, (1, 0): 4, (0, 0): 3, (2, 1): -2})
	 >>> mat2rowdict(M)
	 {0: Vec({0, 1},{0: 3, 1: 1}), 1: Vec({0, 1},{0: 4, 1: 0}), 2: Vec({0, 1},{0: 8, 1: -2})}
	 >>> mat2rowdict(Mat(({0,1},{0,1}),{}))
	 {0: Vec({0, 1},{0: 0, 1: 0}), 1: Vec({0, 1},{0: 0, 1: 0})}
	 """
  return {row:Vec(A.D[1], {col:A[row,col] for col in A.D[1]}) for row in A.D[0]}

def mat2coldict(A):
  """Given a matrix, return a dictionary mapping column labels of A to columns of A
	 e.g.:
	 >>> M = Mat(({0, 1, 2}, {0, 1}), {(0, 1): 1, (2, 0): 8, (1, 0): 4, (0, 0): 3, (2, 1): -2})
	 >>> mat2coldict(M)
	 {0: Vec({0, 1, 2},{0: 3, 1: 4, 2: 8}), 1: Vec({0, 1, 2},{0: 1, 1: 0, 2: -2})}
	 >>> mat2coldict(Mat(({0,1},{0,1}),{}))
	 {0: Vec({0, 1},{0: 0, 1: 0}), 1: Vec({0, 1},{0: 0, 1: 0})}
  """
  return {col:Vec(A.D[0], {row:A[row,col] for row in A.D[0]}) for col in A.D[1]}

def coldict2mat(coldict):
    """
    Given a dictionary or list whose values are Vecs, returns the Mat having these
    Vecs as its columns.  This is the inverse of mat2coldict.
    Assumes all the Vecs have the same label-set.
    Assumes coldict is nonempty.
    If coldict is a dictionary then its keys will be the column-labels of the Mat.
    If coldict is a list then {0...len(coldict)-1} will be the column-labels of the Mat.
    e.g.:
    
    >>> A = {0:Vec({0,1},{0:1,1:2}),1:Vec({0,1},{0:3,1:4})}
    >>> B = [Vec({0,1},{0:1,1:2}),Vec({0,1},{0:3,1:4})]
    >>> mat2coldict(coldict2mat(A)) == A
    True
    >>> coldict2mat(A)
    Mat(({0, 1}, {0, 1}), {(0, 1): 3, (1, 0): 2, (0, 0): 1, (1, 1): 4})
    >>> coldict2mat(A) == coldict2mat(B)
    True
    """
    row_labels = value(coldict).D
    return Mat((row_labels, set(keys(coldict))), {(r,c):coldict[c][r] for c in keys(coldict) for r in row_labels})

def rowdict2mat(rowdict):
    """
    Given a dictionary or list whose values are Vecs, returns the Mat having these
    Vecs as its rows.  This is the inverse of mat2rowdict.
    Assumes all the Vecs have the same label-set.
    Assumes row_dict is nonempty.
    If rowdict is a dictionary then its keys will be the row-labels of the Mat.
    If rowdict is a list then {0...len(rowdict)-1} will be the row-labels of the Mat.
    e.g.:
    
    >>> A = {0:Vec({0,1},{0:1,1:2}),1:Vec({0,1},{0:3,1:4})}
    >>> B = [Vec({0,1},{0:1,1:2}),Vec({0,1},{0:3,1:4})]
    >>> mat2rowdict(rowdict2mat(A)) == A
    True
    >>> rowdict2mat(A)
    Mat(({0, 1}, {0, 1}), {(0, 1): 2, (1, 0): 3, (0, 0): 1, (1, 1): 4})
    >>> rowdict2mat(A) == rowdict2mat(B)
    True
    """
    col_labels = value(rowdict).D
    return Mat((set(keys(rowdict)), col_labels), {(r,c):rowdict[r][c] for r in keys(rowdict) for c in col_labels})

def listlist2mat(L):
  """Given a list of lists of field elements, return a matrix whose ith row consists
  of the elements of the ith list.  The row-labels are {0...len(L)}, and the
  column-labels are {0...len(L[0])}
  >>> A=listlist2mat([[10,20,30,40],[50,60,70,80]])
  >>> print(A)
  <BLANKLINE>
          0  1  2  3
       -------------
   0  |  10 20 30 40
   1  |  50 60 70 80
  <BLANKLINE>
"""
  m,n = len(L), len(L[0])
  return Mat((set(range(m)),set(range(n))), {(r,c):L[r][c] for r in range(m) for c in range(n)})

## Problem 15
def is_superfluous(L, i):
    '''
    Input:
        - L: list of vectors as instances of Vec class
        - i: integer in range(len(L))
    Output:
        True if the span of the vectors of L is the same
        as the span of the vectors of L, excluding L[i].

        False otherwise.
    Examples:
        >>> a0 = Vec({'a','b','c','d'}, {'a':1})
        >>> a1 = Vec({'a','b','c','d'}, {'b':1})
        >>> a2 = Vec({'a','b','c','d'}, {'c':1})
        >>> a3 = Vec({'a','b','c','d'}, {'a':1,'c':3})
        >>> is_superfluous(L, 3)
        True
        >>> is_superfluous([a0,a1,a2,a3], 3)
        True
        >>> is_superfluous([a0,a1,a2,a3], 0)
        True
        >>> is_superfluous([a0,a1,a2,a3], 1)
        False
    '''
    coldict_i = {k:L[k] for k in range(len(L)) if  k!=i }
    mat_i = coldict2mat(coldict_i)
    v = solve(mat_i, L[i])
    res = mat_i * v - L[i]
    res_2 = res*res
    ##print(res_2)
    return res_2 < 1e-14

## Problem 18
def exchange(S, A, z):
    '''
    Input:
        - S: a list of vectors, as instances of your Vec class
        - A: a list of vectors, each of which are in S, with len(A) < len(S)
        - z: an instance of Vec such that A+[z] is linearly independent
    Output: a vector w in S but not in A such that Span S = Span ({z} U S - {w})
    Example:
        >>> S = [list2vec(v) for v in [[0,0,5,3],[2,0,1,3],[0,0,1,0],[1,2,3,4]]]
        >>> A = [list2vec(v) for v in [[0,0,5,3],[2,0,1,3]]]
        >>> z = list2vec([0,2,1,1])
        >>> exchange(S, A, z) == Vec({0, 1, 2, 3},{0: 0, 1: 0, 2: 1, 3: 0})
        True
    '''
    result = z
    for k in range(len(S)):
        s = S[k]
        S_k = [S[x] for x in range(len(S)) if x!=k]
        if not (s in A) and (result==z):
            if is_superfluous([s]+S_k+[z], 0):
                result = s
    return result

##S = [list2vec(v) for v in [[0,0,5,3],[2,0,1,3],[0,0,1,0],[1,2,3,4]]]
##A = [list2vec(v) for v in [[0,0,5,3],[2,0,1,3]]]
##z = list2vec([0,2,1,1])
##vec = exchange(S, A, z)
##print(vec)
##print(vec == Vec({0, 1, 2, 3},{0: 0, 1: 0, 2: 1, 3: 0}))
