from vec import Vec
from GF2 import one
from math import sqrt

from factoring_support import dumb_factor
from factoring_support import intsqrt
from factoring_support import gcd
from factoring_support import primes
from factoring_support import prod

import echelon
import matutil

## Task 1
def int2GF2(i):
    '''
    Returns one if i is odd, 0 otherwise.

    Input:
        - i: an int
    Output:
        - one if i is congruent to 1 mod 2
        - 0   if i is congruent to 0 mod 2
    Examples:
        int2GF2(3)
        one
        int2GF2(100)
        0
    '''
    return 0 if (i%2 == 0) else one

##print(int2GF2(3))
##print(int2GF2(4))

def root_method(n):
    a = intsqrt(n) + 1
    test = intsqrt(a**2 - n)
    while not (test**2 == (a**2 - n)):
        a = a + 1
        test = intsqrt(a**2 - n)
    return (a, test)

##for k in range(16, 100):
##    print(2*k+1, root_method(2*k+1))

##print(146771, root_method(146771))

def gcd(x,y):
    return x if y == 0 else gcd(y, x % y)

N = 367160330145890434494322103
a = 67469780066325164
b = 9429601150488992

##print((a**2 - b**2) % N)
##print(gcd(N, a-b))

primeset={2,3,5,7,11,13, 17}
##for k in [12,154,2*3*3*3*11*11*13,2*17,2*3*5*7*19]:
##    print(dumb_factor(k, primeset))

## Task 2
def make_Vec(primeset, factors):
    '''
    Input:
        - primeset: a set of primes
        - factors: a list of factors [(p_1,a_1), ..., (p_n, a_n)]
                   with p_i in primeset
    Output:
        - a vector v over GF(2) with domain primeset
          such that v[p_i] = int2GF2(a_i) for all i
    Example:
        make_Vec({2,3,11}, [(2,3), (3,2)]) == Vec({2,3,11},{2:one})
        True
    '''
    return Vec(primeset, {p:int2GF2(e) for (p,e) in factors})

## Task 3
def find_candidates(N, primeset):
    '''
    Input:
        - N: an int to factor
        - primeset: a set of primes

    Output:
        - a list [roots, rowlist]
        - roots: a list a_0, a_1, ..., a_n where a_i*a_i - N can be factored
                 over primeset
        - rowlist: a list such that rowlist[i] is a
                   primeset-vector over GF(2) corresponding to a_i
          such that len(roots) = len(rowlist) and len(roots) > len(primeset)
    '''
    a_list = []
    a_factor_vecs = []
    a = intsqrt(N) + 2
    while (len(a_list) <= len(primeset)):
        prime_factors = dumb_factor(a**2 - N, primeset)
        if (len(prime_factors) > 0):
            a_list.append(a)
            ##print(len(a_list), a)
            a_factor_vecs.append(make_Vec(primeset, prime_factors))
        a = a + 1
    return (a_list, a_factor_vecs)

##print(find_candidates(2419, primes(32)))


## Task 4
def find_a_and_b(v, roots, N):
    '''
    Input: 
     - a {0,1,..., n-1}-vector v over GF(2) where n = len(roots)
     - a list roots of integers
     - an integer N to factor
    Output:
      a pair (a,b) of integers
      such that a*a-b*b is a multiple of N
      (if v is correctly chosen)
    '''
    alist = [roots[index] for index in range(len(roots)) if v[index] == one]
    ##print(alist)
    a = prod(alist)
    b = intsqrt(prod([root**2-N for root in alist]))
    return (a,b)

v = Vec({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11},{0: 0, 1: one, 2: one, 4: 0, 5: one, 11: one})
N = 2419
roots = [51, 52, 53, 58, 61, 62, 63, 67, 68, 71, 77, 79]
##print(find_a_and_b(v, roots, N))
v = Vec({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11},{0: 0, 1: 0, 10: one, 2: one})
N = 2419
roots = [51, 52, 53, 58, 61, 62, 63, 67, 68, 71, 77, 79]
##print(find_a_and_b(v, roots, N))


## Task 5
N = 2461799993978700679
##N=243127
primeset = primes(10000)
candidates = find_candidates(N, primeset)
transformation_matrix = echelon.transformation_rows(candidates[1])
(a,b) = find_a_and_b(transformation_matrix[-1], candidates[0], N)
print(a,b)
print(gcd(a-b, N))
smallest_nontrivial_divisor_of_2461799993978700679 = gcd(a-b, N) 
