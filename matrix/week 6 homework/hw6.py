# version code 988
# Please fill out this stencil and submit using the provided submission script.

from matutil import *
from GF2 import one



## Problem 1
# Write each matrix as a list of row lists

echelon_form_1 = [[1,2,0,2,0],
                  [0,1,0,3,4],
                  [0,0,2,3,4],
                  [0,0,0,2,0],
                  [0,0,0,0,4]]

echelon_form_2 = [[0,4,3,4,4],
                  [0,0,4,2,0],
                  [0,0,0,0,1],
                  [0,0,0,0,0]]

echelon_form_3 = [[1,0,0,1],
                  [0,0,0,1],
                  [0,0,0,0]]

echelon_form_4 = [[1,0,0,0],
                  [0,1,0,0],
                  [0,0,0,0],
                  [0,0,0,0]]

def first_non_zero(row):
    result = len(row)
    for index in range(len(row)):
        if not (row[index] == 0):
            result = index
            break
    return result

## Problem 2
def is_echelon(A):
    '''
    Input:
        - A: a list of row lists
    Output:
        - True if A is in echelon form
        - False otherwise
    Examples:
        >>> is_echelon([[1,1,1],[0,1,1],[0,0,1]])
        True
        >>> is_echelon([[0,1,1],[0,1,0],[0,0,1]])
        False
    '''
    result = True
    last_non_zero = -1
    for index in range(len(A)):
        this_non_zero = first_non_zero(A[index])
        if ((this_non_zero <= last_non_zero) and (this_non_zero < len(A[index])) ):
            result = False
            break
        last_non_zero = this_non_zero
    return result

##print(is_echelon([[1,1,1],[0,1,1],[0,0,1]]))
##print(is_echelon([[0,1,1],[0,1,0],[0,0,1]]))

## Problem 3
# Give each answer as a list

echelon_form_vec_a = [1,0,3,0]
echelon_form_vec_b = [-3,0,-2,3]
echelon_form_vec_c = [-5,0,2,0,2]



## Problem 4
# If a solution exists, give it as a list vector.
# If no solution exists, provide "None".

solving_with_echelon_form_a = None
solving_with_echelon_form_b = [21,0,2,0,0]


def first_non_zero(row, label_list):
    result = len(label_list)
    for index in range(len(label_list)):
        if not (row[label_list[index]] == 0):
            result = index
            break
    return result

## Problem 5
def echelon_solve(rowlist, label_list, b):
    '''
    Input:
        - rowlist: a list of Vecs
        - label_list: a list of labels establishing an order on the domain of
                      Vecs in rowlist
        - b: a vector (represented as a list)
    Output:
        - Vec x such that rowlist * x is b
    >>> D = {'A','B','C','D','E'}
    >>> U_rows = [Vec(D, {'A':one, 'E':one}), Vec(D, {'B':one, 'E':one}), Vec(D,{'C':one})] 
    >>> b_list = [one,0,one]>>> cols = ['A', 'B', 'C', 'D', 'E']
    >>> echelon_solve(U_rows, cols, b_list)
    Vec({'B', 'C', 'A', 'D', 'E'},{'B': 0, 'C': one, 'A': one})
    '''
    D = rowlist[0].D
    x = Vec(D, {})
    for row_index in reversed(range(len(rowlist))):
        row = rowlist[row_index]
        index = first_non_zero(row, label_list)
        if (index < len(label_list)):
            c = label_list[index]
            x[c] = (b[row_index] - x*row)/row[c]
    return x

D = {'A','B','C','D','E'}
U_rows = [Vec(D, {'A':one, 'E':one}), Vec(D, {'B':one, 'E':one}), Vec(D,{'C':one})] 
b_list = [one,0,one]
cols = ['A', 'B', 'C', 'D', 'E']
##print(echelon_solve(U_rows, cols, b_list))


## Problem 6
label_list = ['A','B','C','D']
D = set(label_list)
rowlist = [Vec(D, {'A':one, 'B':one, 'D':one}),
           Vec(D, {'B':one}),
           Vec(D, {'C':one}),
           Vec(D, {'D':one})]    # Provide as a list of Vec instances
b = [ one, one, 0, 0 ]          # Provide as a list



## Problem 7
null_space_rows_a = {3,4} # Put the row numbers of M from the PDF



## Problem 8
null_space_rows_b = {4}



## Problem 9
# Write each vector as a list
a = Vec({0,1}, {0:1, 1:2})
b = Vec({0,1}, {0:2, 1:3})
##closest_vector_1 = ((a*b)/(a*a)) * a
closest_vector_1 = [1.6,3.2]

a = Vec({0,1,2}, {1:1})
b = Vec({0,1,2}, {0:1.414, 1:1, 2:1.732})
##closest_vector_2 = ((a*b)/(a*a)) * a
closest_vector_2 = [0,1,0]

a = Vec({0,1,2,3}, {0:-3, 1:-2, 2:-1, 3:4})
b = Vec({0,1,2,3}, {0:7, 1:2, 2:5})
##closest_vector_3 = ((a*b)/(a*a)) * a
closest_vector_3 = [3,2,1,-4]

##print(closest_vector_1)
##print(closest_vector_2)
##print(closest_vector_3)


## Problem 10
# Write each vector as a list

a = Vec({0,1}, {0:3})
b = Vec({0,1}, {0:2, 1:1})
a_para = ((a*b)/(a*a)) * a
a_perp = b-a_para
##print(a_para)
##print(a_perp)

project_onto_1 = [2,0]
projection_orthogonal_1 = [0,1]

a = Vec({0,1,2}, {0:1, 1:2, 2:-1})
b = Vec({0,1,2}, {0:1, 1:1, 2:4})
a_para = ((a*b)/(a*a)) * a
a_perp = b-a_para
##print(a_para)
##print(a_perp)

project_onto_2 = [-1/6, -1/3, 1/6]
projection_orthogonal_2 = [7/6, 4/3, 23/6]

a = Vec({0,1,2}, {0:3, 1:3, 2:12})
b = Vec({0,1,2}, {0:1, 1:1, 2:4})
a_para = ((a*b)/(a*a)) * a
a_perp = b-a_para
##print(a_para)
##print(a_perp)

project_onto_3 = [1,1,4]
projection_orthogonal_3 = [0,0,0]



## Problem 11
norm1 = 3
norm2 = 4
norm3 = 1

